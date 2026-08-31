export class VoiceService {
  private recognition: any = null;
  private isSpeaking = false;
  private onSpeakingChangeCallback: ((speaking: boolean) => void) | null = null;

  constructor() {
    if (typeof window !== 'undefined') {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
      }
    }
  }

  public setSpeakingListener(cb: (speaking: boolean) => void) {
    this.onSpeakingChangeCallback = cb;
  }

  public speak(text: string, language: string = 'en', onEnd?: () => void) {
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      if (onEnd) onEnd();
      return;
    }

    window.speechSynthesis.cancel();

    // Clean LaTeX and markdown markers for clear voice narration
    const cleanText = text
      .replace(/\$([^\$]+)\$/g, '$1')
      .replace(/[\*\#\`\_]/g, '')
      .replace(/\\[a-zA-Z]+/g, ' ')
      .trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);

    // Language selection
    if (language.toLowerCase() === 'hi' || language.toLowerCase() === 'hinglish') {
      utterance.lang = 'hi-IN';
    } else if (language.toLowerCase() === 'bn') {
      utterance.lang = 'bn-IN';
    } else {
      utterance.lang = 'en-US';
    }

    utterance.rate = 0.95;
    utterance.pitch = 1.0;

    utterance.onstart = () => {
      this.isSpeaking = true;
      if (this.onSpeakingChangeCallback) this.onSpeakingChangeCallback(true);
    };

    utterance.onend = () => {
      this.isSpeaking = false;
      if (this.onSpeakingChangeCallback) this.onSpeakingChangeCallback(false);
      if (onEnd) onEnd();
    };

    utterance.onerror = (e) => {
      console.warn('TTS utterance error:', e);
      this.isSpeaking = false;
      if (this.onSpeakingChangeCallback) this.onSpeakingChangeCallback(false);
      if (onEnd) onEnd();
    };

    window.speechSynthesis.speak(utterance);
  }

  public stopSpeaking() {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
      this.isSpeaking = false;
      if (this.onSpeakingChangeCallback) this.onSpeakingChangeCallback(false);
    }
  }

  public startListening(
    language: string = 'en',
    onResult: (transcript: string) => void,
    onError?: (err: any) => void
  ): boolean {
    if (!this.recognition) {
      if (onError) onError(new Error('Speech recognition not supported in this browser.'));
      return false;
    }

    if (language.toLowerCase() === 'hi' || language.toLowerCase() === 'hinglish') {
      this.recognition.lang = 'hi-IN';
    } else if (language.toLowerCase() === 'bn') {
      this.recognition.lang = 'bn-IN';
    } else {
      this.recognition.lang = 'en-US';
    }

    this.recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      onResult(transcript);
    };

    this.recognition.onerror = (err: any) => {
      console.warn('Speech recognition error:', err);
      if (onError) onError(err);
    };

    try {
      this.recognition.start();
      return true;
    } catch (e) {
      console.warn('Recognition start exception:', e);
      return false;
    }
  }

  public stopListening() {
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (e) {
        // ignore
      }
    }
  }
}

export const voiceManager = new VoiceService();
