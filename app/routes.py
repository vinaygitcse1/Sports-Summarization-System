from flask import (render_template, request, jsonify, 
                   redirect, url_for, flash, send_file)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
import json
import time
from app import db
from app.models import User, Summary
from app.nlp_pipeline.summarizer import SportsSummarizer
from app.nlp_pipeline.speech_recognition import AudioProcessor
from .utils import allowed_file
from .forms import LoginForm, RegistrationForm, SummaryForm
from datetime import datetime

# Initialize processors
summarizer = SportsSummarizer()
audio_processor = AudioProcessor()

# Main Blueprint
from flask import Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required

def dashboard():
    # Get user's summaries
    summaries = Summary.query.filter_by(user_id=current_user.id)\
        .order_by(Summary.created_at.desc()).limit(10).all()
    
    # Calculate statistics
    total_summaries = Summary.query.filter_by(user_id=current_user.id).count()
    text_summaries = Summary.query.filter_by(
        user_id=current_user.id, 
        summary_type='text'
    ).count()
    audio_summaries = Summary.query.filter_by(
        user_id=current_user.id, 
        summary_type='audio'
    ).count()
    
    # Calculate average processing time
    avg_time_result = db.session.query(
        db.func.avg(Summary.processing_time)
    ).filter_by(user_id=current_user.id).first()
    avg_processing_time = round(avg_time_result[0] or 0, 2)
    
    return render_template('dashboard.html',
                         summaries=summaries,
                         total_summaries=total_summaries,
                         text_summaries=text_summaries,
                         audio_summaries=audio_summaries,
                         avg_processing_time=avg_processing_time)

@main_bp.route('/summarize', methods=['GET', 'POST'])
@login_required
def summarize():
    form = SummaryForm()
    
    if form.validate_on_submit():
        text = form.text.data
        start_time = time.time()
        
        # Generate summary
        result = summarizer.generate_summary(
            text,
            max_length=form.max_length.data,
            min_length=form.min_length.data
        )
        
        processing_time = time.time() - start_time
        
        # Save to database
        summary = Summary(
            title=form.title.data or "Untitled Summary",
            original_text=text[:5000],  # Limit stored text
            summary_text=result['summary'],
            summary_type='text',
            user_id=current_user.id,
            processing_time=processing_time,
            word_count=result['word_count'],
            key_events=result['key_events']
        )
        
        db.session.add(summary)
        db.session.commit()
        
        return render_template('summary_result.html',
                             summary=result['summary'],
                             key_events=result['key_events'],
                             processing_time=round(processing_time, 2),
                             word_count=result['word_count'])
    
    return render_template('summarize.html', form=form)

@main_bp.route('/audio-summarize', methods=['GET', 'POST'])
@login_required
def audio_summarize():
    if request.method == 'POST':
        if 'audio_file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['audio_file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename, {'mp3', 'wav', 'm4a', 'ogg'}):
            filename = secure_filename(file.filename)
            filepath = os.path.join('uploads', 'audio', filename)
            file.save(filepath)
            
            # Transcribe audio
            start_time = time.time()
            transcription = audio_processor.transcribe_audio(filepath)
            
            if transcription['success']:
                # Generate summary
                result = summarizer.generate_summary(
                    transcription['text'],
                    max_length=150,
                    min_length=50
                )
                
                processing_time = time.time() - start_time
                
                # Save to database
                summary = Summary(
                    title=f"Audio Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    original_text=transcription['text'][:5000],
                    summary_text=result['summary'],
                    summary_type='audio',
                    user_id=current_user.id,
                    processing_time=processing_time,
                    word_count=result['word_count'],
                    key_events=result['key_events']
                )
                
                db.session.add(summary)
                db.session.commit()
                
                # Clean up file
                if os.path.exists(filepath):
                    os.remove(filepath)
                
                return render_template('summary_result.html',
                                     summary=result['summary'],
                                     key_events=result['key_events'],
                                     processing_time=round(processing_time, 2),
                                     word_count=result['word_count'],
                                     source_type='audio')
            else:
                flash(f"Error transcribing audio: {transcription['error']}")
                return redirect(request.url)
    
    return render_template('audio_summarize.html')

# Auth Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        
        flash('Invalid email or password')
    
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# API Blueprint
api_bp = Blueprint('api', __name__)

@api_bp.route('/summarize-text', methods=['POST'])
def api_summarize_text():
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    text = data['text']
    max_length = data.get('max_length', 150)
    min_length = data.get('min_length', 30)
    
    result = summarizer.generate_summary(text, max_length, min_length)
    
    return jsonify({
        'summary': result['summary'],
        'key_events': result['key_events'],
        'word_count': result['word_count'],
        'event_count': result['event_count']
    })

@api_bp.route('/history', methods=['GET'])
@login_required
def get_history():
    summaries = Summary.query.filter_by(user_id=current_user.id)\
        .order_by(Summary.created_at.desc()).all()
    
    history = []
    for summary in summaries:
        history.append({
            'id': summary.id,
            'title': summary.title,
            'summary_preview': summary.summary_text[:100] + '...' if len(summary.summary_text) > 100 else summary.summary_text,
            'type': summary.summary_type,
            'created_at': summary.created_at.strftime('%Y-%m-%d %H:%M'),
            'word_count': summary.word_count,
            'processing_time': summary.processing_time
        })
    
    return jsonify({'history': history})