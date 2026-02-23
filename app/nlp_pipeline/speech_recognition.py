import speech_recognition as sr
from pydub import AudioSegment
import os
import tempfile

class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.supported_formats = ['.mp3', '.wav', '.m4a', '.ogg']
    
    def convert_to_wav(self, audio_path):
        """Convert audio file to WAV format"""
        if audio_path.endswith('.wav'):
            return audio_path
        
        audio = AudioSegment.from_file(audio_path)
        wav_path = audio_path.rsplit('.', 1)[0] + '.wav'
        audio.export(wav_path, format='wav')
        return wav_path
    
    def transcribe_audio(self, audio_path, language='en-US'):
        """Transcribe audio file to text"""
        try:
            # Convert to WAV if needed
            if not audio_path.endswith('.wav'):
                audio_path = self.convert_to_wav(audio_path)
            
            with sr.AudioFile(audio_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = self.recognizer.record(source)
                
                # Transcribe using Google Speech Recognition
                text = self.recognizer.recognize_google(
                    audio_data,
                    language=language
                )
                
                return {
                    'success': True,
                    'text': text,
                    'language': language
                }
        
        except sr.UnknownValueError:
            return {
                'success': False,
                'error': "Could not understand audio"
            }
        except sr.RequestError as e:
            return {
                'success': False,
                'error': f"Speech recognition service error: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Error processing audio: {str(e)}"
            }
    
    def real_time_transcription(self, duration=10, language='en-US'):
        """Real-time transcription from microphone"""
        try:
            with sr.Microphone() as source:
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"Listening for {duration} seconds...")
                
                audio_data = self.recognizer.listen(source, timeout=duration)
                text = self.recognizer.recognize_google(audio_data, language=language)
                
                return {
                    'success': True,
                    'text': text,
                    'duration': duration
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }