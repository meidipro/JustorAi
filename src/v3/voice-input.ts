/**
 * Justor AI — Voice-to-Text Controller
 * Supports native real-time Bengali (bn-BD) and English (en-US) transcription
 * via Web Speech API.
 */

export interface VoiceInputState {
  isListening: boolean;
  recognition: any | null;
}

export function initVoiceInput(
  btnEl: HTMLButtonElement,
  textareaEl: HTMLTextAreaElement,
  language: 'en' | 'bn' = 'en',
  onResult?: (text: string) => void
): () => void {
  const SpeechRecognition =
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

  if (!SpeechRecognition) {
    btnEl.title = language === 'bn' 
      ? 'ভয়েস টাইপিং শুধুমাত্র Chrome, Edge, এবং Safari-তে সমর্থিত' 
      : 'Voice typing is supported in Chrome, Edge, and Safari';
    btnEl.style.opacity = '0.5';
    btnEl.addEventListener('click', () => {
      alert(language === 'bn'
        ? 'আপনার ব্রাউজারে ভয়েস টাইপিং সমর্থিত নয়। দয়া করে Google Chrome বা Edge ব্যবহার করুন।'
        : 'Voice typing is not supported by your current browser. Please use Chrome, Edge, or Safari.');
    });
    return () => {};
  }

  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.lang = language === 'bn' ? 'bn-BD' : 'en-US';

  let isListening = false;
  let finalTranscript = '';

  const stopListening = () => {
    if (isListening) {
      recognition.stop();
      isListening = false;
      btnEl.classList.remove('is-listening');
      btnEl.title = language === 'bn' ? 'ভয়েস টাইপিং শুরু করুন' : 'Click to speak';
    }
  };

  const startListening = () => {
    try {
      finalTranscript = textareaEl.value ? textareaEl.value.trim() + ' ' : '';
      recognition.lang = language === 'bn' ? 'bn-BD' : 'en-US';
      recognition.start();
      isListening = true;
      btnEl.classList.add('is-listening');
      btnEl.title = language === 'bn' ? 'শুনছি... কথা বলুন' : 'Listening... speak now';
    } catch (err) {
      console.warn('[VoiceInput] Start error:', err);
      stopListening();
    }
  };

  recognition.onresult = (event: any) => {
    let interim = '';
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript;
      } else {
        interim += event.results[i][0].transcript;
      }
    }

    const currentText = (finalTranscript + (interim ? ' ' + interim : '')).trim();
    textareaEl.value = currentText;
    
    // Trigger auto-resize on textarea
    textareaEl.dispatchEvent(new Event('input', { bubbles: true }));

    if (onResult) {
      onResult(currentText);
    }
  };

  recognition.onerror = (event: any) => {
    console.warn('[VoiceInput] Recognition error:', event.error);
    stopListening();
  };

  recognition.onend = () => {
    stopListening();
  };

  const toggle = (e: Event) => {
    e.preventDefault();
    e.stopPropagation();
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  btnEl.addEventListener('click', toggle);

  return () => {
    stopListening();
    btnEl.removeEventListener('click', toggle);
  };
}
