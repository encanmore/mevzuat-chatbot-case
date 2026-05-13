import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Mesajlar güncellendikçe otomatik olarak en alta kaydır
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { role: 'user', text: input };
        const botPlaceholder = { role: 'bot', text: '' };

        // Kullanıcı mesajını appendleyip gelecek bot cevabı için placeholder
        setMessages(prev => [...prev, userMessage, botPlaceholder]);
        const currentMessageIndex = messages.length + 1;

        setInput('');
        setLoading(true);

        try {
            const response = await fetch('http://localhost:5000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: input }),
            });

            if (!response.body) return;

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let done = false;
            let accumulatedText = '';

            // Stream processing
            while (!done) {
                const { value, done: doneReading } = await reader.read();
                done = doneReading;
                const chunkValue = decoder.decode(value); // Byte - string conversion
                accumulatedText += chunkValue; // Stringi biriken texte ekle

                setMessages(prev => {
                    const updated = [...prev]; // Önceki mesajları kopyala
                    updated[currentMessageIndex] = { role: 'bot', text: accumulatedText }; // Bot cevabını güncelle
                    return updated;
                });
            }
        } catch (error) {
            console.error("Streaming error:", error);
            setMessages(prev => [
                ...prev.slice(0, -1),
                { role: 'bot', text: "Backend'e bağlantıda bir hata oluştu. FastAPI çalışıyor mu?" }
            ]);
        } finally {
            setLoading(false);
        }
    };

  return (
    <div style={{ maxWidth: '600px', margin: '20px auto', height: '90vh', display: 'flex', flexDirection: 'column', border: '1px solid #ddd', borderRadius: '8px', overflow: 'hidden', backgroundColor: '#f9f9f9' }}>
      <div style={{ padding: '15px', backgroundColor: '#007bff', color: 'white', textAlign: 'center', fontWeight: 'bold' }}>
        Mevzuat Chatbot
      </div>
      
      <div style={{ flex: 1, padding: '15px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {messages.map((msg, index) => (
          <div key={index} style={{ alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '80%', padding: '10px', borderRadius: '15px', backgroundColor: msg.role === 'user' ? '#007bff' : '#eee', color: msg.role === 'user' ? 'white' : 'black' }}>
                {/* ChatGPT ve birçok diğer LLM Markdown şeklinde cevap verdiği için Markdown renderla */} }
                {msg.role === 'bot' ? (
                    <ReactMarkdown>{msg.text}</ReactMarkdown>
                ) : (
                    msg.text
                )}
          </div>
        ))}
        {loading && <div style={{ fontStyle: 'italic', color: '#888' }}>Düşünüyor...</div>}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} style={{ padding: '15px', borderTop: '1px solid #ddd', display: 'flex', gap: '10px' }}>
        <input 
          value={input} 
          onChange={(e) => setInput(e.target.value)} 
          placeholder="Sorunuzu buraya yazın..." 
          style={{ flex: 1, padding: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
        />
        <button type="submit" style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          Gönder
        </button>
      </form>
    </div>
  );
}

export default App;