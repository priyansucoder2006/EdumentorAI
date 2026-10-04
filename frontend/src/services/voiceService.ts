export interface VoiceSettings {
  rate: number;
  pitch: number;
  voiceName: string | null;
}

export class VoiceService {
  private recognition: any = null;
  private isSpeaking = false;
  private onSpeakingChangeCallback: ((speaking: boolean) => void) | null = null;
  private voices: SpeechSynthesisVoice[] = [];
  private keepAliveInterval: any = null;
  private preferredVoiceName: string | null = null;
  private preferredRate: number = 0.98;
  private preferredPitch: number = 1.05;

  constructor() {
    if (typeof window !== 'undefined') {
      // Speech recognition
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
      }

      // Load saved settings
      try {
        this.preferredVoiceName = localStorage.getItem('edumentor_voice_name');
        const savedRate = localStorage.getItem('edumentor_voice_rate');
        if (savedRate) this.preferredRate = parseFloat(savedRate) || 0.98;
        const savedPitch = localStorage.getItem('edumentor_voice_pitch');
        if (savedPitch) this.preferredPitch = parseFloat(savedPitch) || 1.05;
      } catch (e) {
        // ignore
      }

      // Load voices
      this.initVoices();
    }
  }

  private initVoices() {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;

    const loadVoices = () => {
      this.voices = window.speechSynthesis.getVoices();
    };

    loadVoices();
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }
  }

  public getAvailableVoices(): SpeechSynthesisVoice[] {
    if (this.voices.length === 0 && typeof window !== 'undefined' && window.speechSynthesis) {
      this.voices = window.speechSynthesis.getVoices();
    }
    return this.voices;
  }

  public getVoiceSettings(): VoiceSettings {
    return {
      rate: this.preferredRate,
      pitch: this.preferredPitch,
      voiceName: this.preferredVoiceName,
    };
  }

  public setVoiceSettings(settings: Partial<VoiceSettings>) {
    if (settings.rate !== undefined) {
      this.preferredRate = settings.rate;
      try {
        localStorage.setItem('edumentor_voice_rate', String(settings.rate));
      } catch {}
    }
    if (settings.pitch !== undefined) {
      this.preferredPitch = settings.pitch;
      try {
        localStorage.setItem('edumentor_voice_pitch', String(settings.pitch));
      } catch {}
    }
    if (settings.voiceName !== undefined) {
      this.preferredVoiceName = settings.voiceName;
      try {
        if (settings.voiceName) {
          localStorage.setItem('edumentor_voice_name', settings.voiceName);
        } else {
          localStorage.removeItem('edumentor_voice_name');
        }
      } catch {}
    }
  }

  /**
   * Intelligently selects the most appropriate, natural-sounding voice for Prof. Elena.
   * Strictly avoids harsh, robotic male voices (e.g. Microsoft David) and prioritizes
   * natural, articulate female educational voices.
   */
  public selectBestVoice(language: string = 'en'): SpeechSynthesisVoice | null {
    const allVoices = this.getAvailableVoices();
    if (allVoices.length === 0) return null;

    // 1. If user explicitly chose a voice, try to respect it
    if (this.preferredVoiceName) {
      const explicit = allVoices.find((v) => v.name === this.preferredVoiceName);
      if (explicit) return explicit;
    }

    const langLower = language.toLowerCase();
    const isHinglish = langLower === 'hinglish';
    const isHindi = langLower === 'hi' || langLower.startsWith('hi-');
    const isBengali = langLower === 'bn' || langLower.startsWith('bn-');

    // List of known robotic or male voices to strictly deprioritize
    const isRoboticOrMale = (name: string): boolean => {
      const n = name.toLowerCase();
      return (
        n.includes('david') ||
        n.includes('mark') ||
        n.includes('george') ||
        n.includes('hazel') ||
        n.includes('richard') ||
        n.includes('male') ||
        n.includes('espeak')
      );
    };

    // Female indicator
    const isFemale = (name: string): boolean => {
      const n = name.toLowerCase();
      return (
        n.includes('female') ||
        n.includes('aria') ||
        n.includes('jenny') ||
        n.includes('neerja') ||
        n.includes('swara') ||
        n.includes('zira') ||
        n.includes('samantha') ||
        n.includes('karen') ||
        n.includes('victoria') ||
        n.includes('moira') ||
        n.includes('elena') ||
        n.includes('siri') ||
        n.includes('kalpana') ||
        n.includes('natural')
      );
    };

    // Case A: Hinglish - Needs Indian English natural female voice so both English & Hindi sound crystal clear
    if (isHinglish) {
      // 1. Microsoft Neerja (Online Natural Indian English) or Google Indian English
      const indianFemale = allVoices.find(
        (v) =>
          (v.lang.startsWith('en-IN') || v.name.toLowerCase().includes('india')) &&
          isFemale(v.name) &&
          !isRoboticOrMale(v.name)
      );
      if (indianFemale) return indianFemale;

      // 2. Any en-IN voice
      const anyIndian = allVoices.find((v) => v.lang.startsWith('en-IN') && !isRoboticOrMale(v.name));
      if (anyIndian) return anyIndian;

      // 3. Fallback to top-tier Natural English female voice
      const premiumFemale = allVoices.find(
        (v) =>
          (v.name.toLowerCase().includes('aria') ||
            v.name.toLowerCase().includes('jenny') ||
            v.name.toLowerCase().includes('google uk english female') ||
            v.name.toLowerCase().includes('samantha')) &&
          !isRoboticOrMale(v.name)
      );
      if (premiumFemale) return premiumFemale;
    }

    // Case B: Hindi (Pure Hindi)
    if (isHindi) {
      const hindiFemale = allVoices.find(
        (v) =>
          (v.lang.startsWith('hi') || v.name.toLowerCase().includes('hindi')) &&
          isFemale(v.name) &&
          !isRoboticOrMale(v.name)
      );
      if (hindiFemale) return hindiFemale;

      const anyHindi = allVoices.find((v) => v.lang.startsWith('hi'));
      if (anyHindi) return anyHindi;
    }

    // Case C: Bengali
    if (isBengali) {
      const bengaliVoice = allVoices.find((v) => v.lang.startsWith('bn'));
      if (bengaliVoice) return bengaliVoice;
    }

    // Case D: Standard English / Default: Prioritize natural female voices for Prof. Elena
    // Priority order:
    // 1. Microsoft Aria Online (Natural)
    // 2. Microsoft Jenny Online (Natural)
    // 3. Google UK English Female / Google US English
    // 4. Samantha (macOS)
    // 5. Microsoft Zira (Windows default female)
    // 6. Any female English voice
    const topPicks = [
      (v: SpeechSynthesisVoice) => v.name.includes('Aria') && v.name.includes('Natural'),
      (v: SpeechSynthesisVoice) => v.name.includes('Jenny') && v.name.includes('Natural'),
      (v: SpeechSynthesisVoice) => v.name.toLowerCase().includes('uk english female'),
      (v: SpeechSynthesisVoice) => v.name.includes('Samantha'),
      (v: SpeechSynthesisVoice) => v.name.includes('Zira'),
      (v: SpeechSynthesisVoice) => v.name.includes('Natural') && isFemale(v.name),
      (v: SpeechSynthesisVoice) => v.lang.startsWith('en') && isFemale(v.name) && !isRoboticOrMale(v.name),
      (v: SpeechSynthesisVoice) => isFemale(v.name) && !isRoboticOrMale(v.name),
      (v: SpeechSynthesisVoice) => v.lang.startsWith('en') && !isRoboticOrMale(v.name),
    ];

    for (const matcher of topPicks) {
      const match = allVoices.find(matcher);
      if (match) return match;
    }

    // Absolute fallback: first non-robotic voice or default
    return allVoices.find((v) => !isRoboticOrMale(v.name)) || allVoices[0] || null;
  }

  /**
   * Preprocesses academic text, LaTeX formulas, and Markdown symbols so
   * speech synthesis sounds like a natural, eloquent human mentor.
   */
  public cleanTextForSpeech(text: string): string {
    if (!text) return '';

    let clean = text;

    // 1. Remove markdown bold, italic, code blocks, headers
    clean = clean.replace(/```[\s\S]*?```/g, ' [code demonstration] ');
    clean = clean.replace(/`([^`]+)`/g, '$1');
    clean = clean.replace(/\*\*([^\*]+)\*\*/g, '$1');
    clean = clean.replace(/\*([^\*]+)\*/g, '$1');
    clean = clean.replace(/_([^_]+)_/g, '$1');
    clean = clean.replace(/#{1,6}\s+/g, '');
    clean = clean.replace(/^\s*[-*+]\s+/gm, '');
    clean = clean.replace(/^\s*\d+\.\s+/gm, '');

    // 2. Clean mathematical equations & units for conversational pronunciation
    clean = clean.replace(/m\/s\^2/gi, ' meters per second squared ');
    clean = clean.replace(/m\/s\b/gi, ' meters per second ');
    clean = clean.replace(/km\/h\b/gi, ' kilometers per hour ');
    clean = clean.replace(/\^2\b/g, ' squared ');
    clean = clean.replace(/\^3\b/g, ' cubed ');
    clean = clean.replace(/\bF\s*=\s*ma\b/gi, ' F equals m times a ');
    clean = clean.replace(/\bV\s*=\s*IR\b/gi, ' V equals I times R ');

    // 3. LaTeX symbols
    clean = clean.replace(/\$([^\$]+)\$/g, '$1');
    clean = clean.replace(/\$\$([^\$]+)\$\$/g, '$1');
    clean = clean.replace(/\\cdot/g, ' times ');
    clean = clean.replace(/\\times/g, ' times ');
    clean = clean.replace(/\\frac\{([^}]+)\}\{([^}]+)\}/g, '$1 over $2');
    clean = clean.replace(/\\sqrt\{([^}]+)\}/g, ' square root of $1 ');
    clean = clean.replace(/\\approx/g, ' approximately ');
    clean = clean.replace(/\\neq/g, ' does not equal ');
    clean = clean.replace(/\\le/g, ' less than or equal to ');
    clean = clean.replace(/\\ge/g, ' greater than or equal to ');
    clean = clean.replace(/\\Delta/g, ' delta ');
    clean = clean.replace(/\\[a-zA-Z]+/g, ' ');

    // 4. Remove emojis and unwanted symbols
    clean = clean.replace(
      /[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F700}-\u{1F77F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu,
      ''
    );

    // 5. Normalize whitespace and punctuation pauses
    clean = clean.replace(/\s+/g, ' ').trim();

    return clean;
  }

  public setSpeakingListener(cb: (speaking: boolean) => void) {
    this.onSpeakingChangeCallback = cb;
  }

  public speak(text: string, language: string = 'en', onEnd?: () => void) {
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      if (onEnd) onEnd();
      return;
    }

    this.stopSpeaking();

    const cleanText = this.cleanTextForSpeech(text);
    if (!cleanText) {
      if (onEnd) onEnd();
      return;
    }

    const utterance = new SpeechSynthesisUtterance(cleanText);

    // 1. Dynamically select the best natural female voice
    const bestVoice = this.selectBestVoice(language);
    if (bestVoice) {
      utterance.voice = bestVoice;
      utterance.lang = bestVoice.lang;
    } else {
      // Fallback language tag
      const langLower = language.toLowerCase();
      if (langLower === 'hi') {
        utterance.lang = 'hi-IN';
      } else if (langLower === 'hinglish') {
        // Indian English accent for Hinglish
        utterance.lang = 'en-IN';
      } else if (langLower === 'bn') {
        utterance.lang = 'bn-IN';
      } else {
        utterance.lang = 'en-US';
      }
    }

    utterance.rate = this.preferredRate;
    utterance.pitch = this.preferredPitch;

    utterance.onstart = () => {
      this.isSpeaking = true;
      if (this.onSpeakingChangeCallback) this.onSpeakingChangeCallback(true);

      // Chrome 15s keep-alive hack: periodically resume synthesis so Chrome does not freeze
      if (this.keepAliveInterval) clearInterval(this.keepAliveInterval);
      this.keepAliveInterval = setInterval(() => {
        if (typeof window !== 'undefined' && window.speechSynthesis.speaking) {
          window.speechSynthesis.pause();
          window.speechSynthesis.resume();
        }
      }, 10000);
    };

    const cleanup = () => {
      this.isSpeaking = false;
      if (this.keepAliveInterval) {
        clearInterval(this.keepAliveInterval);
        this.keepAliveInterval = null;
      }
      if (this.onSpeakingChangeCallback) this.onSpeakingChangeCallback(false);
    };

    utterance.onend = () => {
      cleanup();
      if (onEnd) onEnd();
    };

    utterance.onerror = (e) => {
      // SpeechSynthesis cancel generates an 'interrupted' error which is expected
      if (e.error !== 'interrupted' && e.error !== 'canceled') {
        console.warn('TTS utterance error:', e);
      }
      cleanup();
      if (onEnd) onEnd();
    };

    try {
      window.speechSynthesis.speak(utterance);
    } catch (e) {
      console.warn('Error invoking speechSynthesis.speak:', e);
      cleanup();
      if (onEnd) onEnd();
    }
  }

  public testVoice(sampleText?: string, language: string = 'en') {
    const text =
      sampleText ||
      "Hello! I am Professor Elena, your adaptive AI teacher. I'm calibrated to explain concepts step by step with interactive checks. Let's master this topic together!";
    this.speak(text, language);
  }

  public stopSpeaking() {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
      this.isSpeaking = false;
      if (this.keepAliveInterval) {
        clearInterval(this.keepAliveInterval);
        this.keepAliveInterval = null;
      }
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

    const langLower = language.toLowerCase();
    if (langLower === 'hi') {
      this.recognition.lang = 'hi-IN';
    } else if (langLower === 'hinglish') {
      this.recognition.lang = 'en-IN';
    } else if (langLower === 'bn') {
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

