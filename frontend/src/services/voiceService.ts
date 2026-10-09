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
  private voicesChangedListeners: Array<() => void> = [];

  constructor() {
    if (typeof window !== 'undefined') {
      // Speech recognition setup
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
        // ignore storage errors
      }

      // Initialize speech synthesis voices
      this.initVoices();
    }
  }

  private initVoices() {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;

    const loadVoices = () => {
      const v = window.speechSynthesis.getVoices();
      if (v && v.length > 0) {
        this.voices = v;
        this.voicesChangedListeners.forEach((cb) => {
          try {
            cb();
          } catch {}
        });
      }
    };

    loadVoices();

    // Standard event listener
    try {
      window.speechSynthesis.addEventListener('voiceschanged', loadVoices);
    } catch {}

    // Fallback property assignment
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    // Chrome async recovery check
    setTimeout(loadVoices, 300);
    setTimeout(loadVoices, 1000);
  }

  public subscribeVoicesChanged(callback: () => void): () => void {
    this.voicesChangedListeners.push(callback);
    return () => {
      this.voicesChangedListeners = this.voicesChangedListeners.filter((cb) => cb !== callback);
    };
  }

  public getAvailableVoices(): SpeechSynthesisVoice[] {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      const live = window.speechSynthesis.getVoices();
      if (live && live.length > 0) {
        this.voices = live;
      }
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
   * Retrieves user-selected voice for a specific language (e.g. 'en', 'bn', 'hi')
   */
  public getPreferredVoiceForLanguage(language: string = 'en'): string | null {
    const langKey = language.toLowerCase().split('-')[0];
    try {
      const specific = localStorage.getItem(`edumentor_voice_name_${langKey}`);
      if (specific) return specific;
    } catch {}
    return this.preferredVoiceName;
  }

  /**
   * Sets preferred voice for a specific language
   */
  public setPreferredVoiceForLanguage(language: string = 'en', voiceName: string | null) {
    const langKey = language.toLowerCase().split('-')[0];
    try {
      if (voiceName) {
        localStorage.setItem(`edumentor_voice_name_${langKey}`, voiceName);
        localStorage.setItem('edumentor_voice_name', voiceName);
        this.preferredVoiceName = voiceName;
      } else {
        localStorage.removeItem(`edumentor_voice_name_${langKey}`);
      }
    } catch {}
  }

  /**
   * Clears saved preference for language
   */
  public clearPreferredVoiceForLanguage(language: string = 'en') {
    const langKey = language.toLowerCase().split('-')[0];
    try {
      localStorage.removeItem(`edumentor_voice_name_${langKey}`);
    } catch {}
  }

  /**
   * Intelligently selects the most appropriate, natural-sounding voice for Prof. Elena.
   * Isolates voices by language to prevent silent/garbled playback across language switches.
   */
  public selectBestVoice(language: string = 'en'): SpeechSynthesisVoice | null {
    const allVoices = this.getAvailableVoices();
    if (allVoices.length === 0) return null;

    const langLower = (language || 'en').toLowerCase().trim();
    const langPrefix = langLower.split('-')[0];

    // Helper functions for voice attributes
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

    const isFemale = (name: string): boolean => {
      const n = name.toLowerCase();
      return (
        n.includes('female') ||
        n.includes('aria') ||
        n.includes('jenny') ||
        n.includes('zira') ||
        n.includes('samantha') ||
        n.includes('karen') ||
        n.includes('victoria') ||
        n.includes('moira') ||
        n.includes('elena') ||
        n.includes('siri') ||
        n.includes('tanishaa') ||
        n.includes('swara') ||
        n.includes('natural')
      );
    };

    const isVoiceMatchingLang = (v: SpeechSynthesisVoice, prefix: string): boolean => {
      const vl = v.lang.toLowerCase();
      const vn = v.name.toLowerCase();
      if (prefix === 'bn') {
        return vl.startsWith('bn') || vn.includes('bengali') || vn.includes('bangla');
      }
      if (prefix === 'hi') {
        return vl.startsWith('hi') || vn.includes('hindi');
      }
      if (prefix === 'en') {
        return vl.startsWith('en');
      }
      return vl.startsWith(prefix);
    };

    // 1. Check user preference for this language
    const preferredName = this.getPreferredVoiceForLanguage(language);
    if (preferredName) {
      const explicit = allVoices.find((v) => v.name === preferredName);
      // Validate that this explicit voice actually supports the requested language
      if (explicit && isVoiceMatchingLang(explicit, langPrefix)) {
        return explicit;
      }
    }

    // 2. Language-specific matching
    if (langPrefix === 'bn') {
      // Bengali
      const bengaliFemale = allVoices.find(
        (v) => isVoiceMatchingLang(v, 'bn') && isFemale(v.name)
      );
      if (bengaliFemale) return bengaliFemale;

      const bengaliAny = allVoices.find((v) => isVoiceMatchingLang(v, 'bn'));
      if (bengaliAny) return bengaliAny;
    } else if (langPrefix === 'hi') {
      // Hindi
      const hindiFemale = allVoices.find(
        (v) => isVoiceMatchingLang(v, 'hi') && isFemale(v.name)
      );
      if (hindiFemale) return hindiFemale;

      const hindiAny = allVoices.find((v) => isVoiceMatchingLang(v, 'hi'));
      if (hindiAny) return hindiAny;
    }

    // 3. English or general fallback
    // Priority list for Prof. Elena:
    const topEnglishPicks = [
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

    if (langPrefix === 'en') {
      for (const matcher of topEnglishPicks) {
        const match = allVoices.find(matcher);
        if (match) return match;
      }
    } else {
      // Check for any voice in target language
      const langMatch = allVoices.find((v) => isVoiceMatchingLang(v, langPrefix) && !isRoboticOrMale(v.name));
      if (langMatch) return langMatch;
    }

    // Fallback: first non-robotic voice or first available
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

    // 4. Remove emojis
    clean = clean.replace(
      /[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F700}-\u{1F77F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu,
      ''
    );

    // 5. Normalize whitespace
    clean = clean.replace(/\s+/g, ' ').trim();

    return clean;
  }

  public setSpeakingListener(cb: (speaking: boolean) => void) {
    this.onSpeakingChangeCallback = cb;
  }

  public getIsSpeaking(): boolean {
    return this.isSpeaking;
  }

  /**
   * Audition / preview a specific voice immediately with an appropriate native greeting
   */
  public previewVoice(
    voice: SpeechSynthesisVoice,
    sampleText?: string,
    onEnd?: () => void
  ) {
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      if (onEnd) onEnd();
      return;
    }

    this.stopSpeaking();

    const isBengali =
      voice.lang.toLowerCase().startsWith('bn') ||
      voice.name.toLowerCase().includes('bengali') ||
      voice.name.toLowerCase().includes('bangla');
    const isHindi = voice.lang.toLowerCase().startsWith('hi');

    let text = sampleText;
    if (!text) {
      if (isBengali) {
        text = "নমস্কার! আমি প্রফেসর এলেনা, আপনার এআই শিক্ষিকা।";
      } else if (isHindi) {
        text = "नमस्ते! मैं प्रोफेसर एलेना हूँ, आपकी AI शिक्षिका।";
      } else {
        text = "Hello! I am Professor Elena, your adaptive AI teacher.";
      }
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = voice;
    utterance.lang = voice.lang;
    utterance.rate = this.preferredRate;
    utterance.pitch = this.preferredPitch;

    utterance.onstart = () => {
      this.isSpeaking = true;
      if (this.onSpeakingChangeCallback) this.onSpeakingChangeCallback(true);
    };

    const cleanup = () => {
      this.isSpeaking = false;
      if (this.onSpeakingChangeCallback) this.onSpeakingChangeCallback(false);
      if (onEnd) onEnd();
    };

    utterance.onend = cleanup;
    utterance.onerror = cleanup;

    // Small delay to ensure browser cancel queue is resolved
    setTimeout(() => {
      try {
        if (window.speechSynthesis.paused) {
          window.speechSynthesis.resume();
        }
        window.speechSynthesis.speak(utterance);
      } catch (e) {
        console.warn('Voice preview error:', e);
        cleanup();
      }
    }, 25);
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

    // 1. Dynamically select the best natural voice for the target language
    const bestVoice = this.selectBestVoice(language);
    if (bestVoice) {
      utterance.voice = bestVoice;
      utterance.lang = bestVoice.lang;
    } else {
      const langLower = language.toLowerCase();
      if (langLower === 'bn' || langLower.startsWith('bn')) {
        utterance.lang = 'bn-IN';
      } else if (langLower === 'hi' || langLower.startsWith('hi')) {
        utterance.lang = 'hi-IN';
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
      if (e.error !== 'interrupted' && e.error !== 'canceled') {
        console.warn('TTS utterance error:', e);
      }
      cleanup();
      if (onEnd) onEnd();
    };

    // Chrome race condition protection: schedule speech after cancel
    setTimeout(() => {
      try {
        if (typeof window !== 'undefined' && window.speechSynthesis.paused) {
          window.speechSynthesis.resume();
        }
        window.speechSynthesis.speak(utterance);
      } catch (e) {
        console.warn('Error invoking speechSynthesis.speak:', e);
        cleanup();
        if (onEnd) onEnd();
      }
    }, 25);
  }

  public testVoice(sampleText?: string, language: string = 'en', onEnd?: () => void) {
    const langLower = (language || 'en').toLowerCase();
    let text = sampleText;
    if (!text) {
      if (langLower.startsWith('bn')) {
        text = "নমস্কার! আমি প্রফেসর এলেনা, আপনার এআই শিক্ষিকা। চলুন বিষয়টি একসাথে নিখুঁতভাবে শিখি!";
      } else if (langLower.startsWith('hi')) {
        text = "नमस्ते! मैं प्रोफेसर एलेना हूँ, आपकी AI शिक्षिका। चलिए इस विषय को एक साथ सीखते हैं!";
      } else {
        text = "Hello! I am Professor Elena, your adaptive AI teacher. I'm calibrated to explain concepts step by step with interactive checks. Let's master this topic together!";
      }
    }
    this.speak(text, language, onEnd);
  }

  public stopSpeaking() {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
      }
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
    if (langLower === 'bn' || langLower.startsWith('bn')) {
      this.recognition.lang = 'bn-IN';
    } else if (langLower === 'hi' || langLower.startsWith('hi')) {
      this.recognition.lang = 'hi-IN';
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


