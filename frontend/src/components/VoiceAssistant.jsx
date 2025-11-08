import React, { useState, useEffect, useRef } from 'react';
import './VoiceAssistant.css';

function VoiceAssistant() {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [response, setResponse] = useState('');
    const [isSupported, setIsSupported] = useState(false);
    const recognitionRef = useRef(null);
    const synthRef = useRef(null);

    // --- Move speak and processCommand above useEffect ---
    const speak = React.useCallback((text) => {
        if (synthRef.current) {
            // Cancel any ongoing speech
            synthRef.current.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;
            synthRef.current.speak(utterance);
        }
    }, []);

    const processCommand = React.useCallback(async(command) => {
        const lowerCommand = command.toLowerCase();
        let responseText = '';
        // Command patterns
        if (lowerCommand.includes('show') && lowerCommand.includes('regulator')) {
            responseText = 'Showing regulatory updates';
            window.location.href = '/dashboard?team=regulator';
        } else if (lowerCommand.includes('show') && lowerCommand.includes('investor')) {
            responseText = 'Showing investor intelligence';
            window.location.href = '/dashboard?team=investor';
        } else if (lowerCommand.includes('show') && lowerCommand.includes('competitor')) {
            responseText = 'Showing competitive intelligence';
            window.location.href = '/dashboard?team=competitor';
        } else if (lowerCommand.includes('show') && lowerCommand.includes('research')) {
            responseText = 'Showing research updates';
            window.location.href = '/dashboard?team=researcher';
        } else if (lowerCommand.includes('search') || lowerCommand.includes('find')) {
            const searchTerm = extractSearchTerm(lowerCommand);
            responseText = `Searching for ${searchTerm}`;
            // Trigger search in dashboard
            window.dispatchEvent(new CustomEvent('voiceSearch', { detail: searchTerm }));
        } else if (lowerCommand.includes('activate') && lowerCommand.includes('scout')) {
            responseText = 'Scouting mode activated. Install the browser extension to start scouting.';
        } else if (lowerCommand.includes('pricing') || lowerCommand.includes('upgrade')) {
            responseText = 'Taking you to pricing plans';
            window.location.href = '/pricing';
        } else if (lowerCommand.includes('profile') || lowerCommand.includes('settings')) {
            responseText = 'Opening your profile';
            window.location.href = '/profile';
        } else if (lowerCommand.includes('help')) {
            responseText = 'You can say: Show me regulator updates, Search for AI news, Activate scouting mode, Go to pricing, or Open profile.';
        } else {
            responseText = 'I didn\'t understand that command. Try saying: Show me investor updates, or Search for funding news.';
        }
        setResponse(responseText);
        speak(responseText);
    }, [speak]);

    const extractSearchTerm = (command) => {
        // Extract search term from commands like "search for AI" or "find venture capital"
        const patterns = [
            /search for (.+)/i,
            /find (.+)/i,
            /look for (.+)/i,
            /show me (.+)/i
        ];
        for (const pattern of patterns) {
            const match = command.match(pattern);
            if (match && match[1]) {
                return match[1];
            }
        }
        return 'information';
    };

    useEffect(() => {
        // Check if browser supports Speech Recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const SpeechSynthesis = window.speechSynthesis;
        if (SpeechRecognition && SpeechSynthesis) {
            setIsSupported(true);
            // Initialize recognition
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = false;
            recognitionRef.current.interimResults = false;
            recognitionRef.current.lang = 'en-US';
            recognitionRef.current.onresult = (event) => {
                const result = event.results[0][0].transcript;
                setTranscript(result);
                processCommand(result);
            };
            recognitionRef.current.onerror = () => {
                setIsListening(false);
                setResponse('Sorry, I didn\'t catch that. Please try again.');
            };
            recognitionRef.current.onend = () => {
                setIsListening(false);
            };
            synthRef.current = SpeechSynthesis;
        }
        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.abort();
            }
            if (synthRef.current) {
                synthRef.current.cancel();
            }
        };
    }, [processCommand]);

    const startListening = () => {
        if (recognitionRef.current && !isListening) {
            setTranscript('');
            setResponse('');
            recognitionRef.current.start();
            setIsListening(true);
        }
    };

    const stopListening = () => {
        if (recognitionRef.current && isListening) {
            recognitionRef.current.stop();
            setIsListening(false);
        }
    };

    if (!isSupported) {
        return null; // Don't render if not supported
    }

    return (
        <div className="voice-assistant">
            <button
                className={`voice-button ${isListening ? 'listening' : ''}`}
                onClick={isListening ? stopListening : startListening}
                title="Voice Assistant"
            >
                {isListening ? (
                    <svg className="voice-icon pulse" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
                        <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
                    </svg>
                ) : (
                    <svg className="voice-icon" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
                        <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
                    </svg>
                )}
            </button>
            {(transcript || response) && (
                <div className="voice-feedback">
                    {transcript && (
                        <div className="voice-transcript">
                            <strong>You said:</strong> &quot;{transcript}&quot;
                        </div>
                    )}
                    {response && (
                        <div className="voice-response">
                            <strong>Response:</strong> {response}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default VoiceAssistant;