import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, FileText, Activity, Server, AlertCircle, Trash2 } from 'lucide-react';

const API_URL = 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY;

const generateSessionId = () => `session-${Math.random().toString(36).substring(2, 9)}`;

function App() {
  const [sessionId, setSessionId] = useState(generateSessionId());
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [logs, setLogs] = useState([{ time: new Date().toISOString(), message: 'System initialized. Waiting for API connection...' }]);
  const [sessionData, setSessionData] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const logsEndRef = useRef(null);

  const endChat = () => {
    const newSessionId = generateSessionId();
    setSessionId(newSessionId);
    setMessages([]);
    setSessionData(null);
    setInputValue('');
    addLog(`Session ended. Started new session: ${newSessionId}`);
  };

  const addLog = (message) => {
    setLogs((prev) => [...prev, { time: new Date().toISOString(), message }]);
  };

  const scrollToBottom = (ref) => {
    ref.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom(messagesEndRef);
  }, [messages, isTyping]);

  useEffect(() => {
    scrollToBottom(logsEndRef);
  }, [logs]);

  const fetchSessionData = async () => {
    try {
      addLog(`Fetching session intelligence for ${sessionId}...`);
      const response = await axios.get(`${API_URL}/api/session/${sessionId}`, {
        headers: { 'x-api-key': API_KEY }
      });
      setSessionData(response.data);
      addLog('Session data retrieved successfully.');
    } catch (error) {
      console.error('Failed to fetch session info', error);
      addLog(`Error fetching session data: ${error.message}`);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const newMessage = {
      sender: 'scammer',
      text: inputValue,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, newMessage]);
    setInputValue('');
    setIsTyping(true);
    addLog(`Sending message to Honeypot API...`);

    try {
      const response = await axios.post(`${API_URL}/api/honeypot`, {
        sessionId: sessionId,
        message: newMessage,
        conversationHistory: messages
      }, {
        headers: { 'x-api-key': API_KEY }
      });

      addLog(`API Connected. Received response.`);
      const botMessage = {
        sender: 'user', // The honeypot poses as the user
        text: response.data.reply,
        timestamp: Date.now(),
      };
      
      setMessages((prev) => [...prev, botMessage]);
      addLog('Message processed by Agentic Honeypot.');
      
      // Fetch updated session intelligence
      await fetchSessionData();
      
    } catch (error) {
      console.error('API Error:', error);
      addLog(`API Request Failed: ${error.message}`);
      setMessages((prev) => [...prev, {
        sender: 'system',
        text: `Error connecting to API. Please ensure the backend is running on ${API_URL}`,
        timestamp: Date.now(),
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const formatTime = (ts) => {
    const d = new Date(ts);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex h-screen bg-gray-900 text-gray-100 font-sans overflow-hidden">
      
      {/* LEFT PANE - Intelligence / Txt File View */}
      <div className="w-1/4 border-r border-gray-700 bg-gray-900 flex flex-col">
        <div className="p-4 bg-gray-800 border-b border-gray-700 flex items-center gap-2">
          <FileText size={20} className="text-blue-400" />
          <h2 className="font-semibold text-lg">intelligence.txt</h2>
        </div>
        <div className="p-4 flex-1 overflow-y-auto font-mono text-sm text-green-400 whitespace-pre-wrap">
          {sessionData ? (
            <div>
              <p className="text-gray-400"># SESSION REPORT</p>
              <p>Session ID: {sessionData.session_id}</p>
              <p>Message Count: {sessionData.message_count}</p>
              <p className={sessionData.scam_detected ? 'text-red-400 font-bold' : 'text-gray-400'}>
                Scam Detected: {sessionData.scam_detected ? 'YES' : 'NO'}
              </p>
              {sessionData.scam_detected && (
                <>
                  <p className="text-red-300">Type: {sessionData.scam_type}</p>
                  <p className="text-red-300">Confidence: {(sessionData.confidence * 100).toFixed(1)}%</p>
                </>
              )}
              
              <p className="text-gray-400 mt-4"># EXTRACTED DATA</p>
              <p>Bank Accounts: {sessionData.intelligence?.bankAccounts?.join(', ') || 'None'}</p>
              <p>UPI IDs: {sessionData.intelligence?.upiIds?.join(', ') || 'None'}</p>
              <p>Phones: {sessionData.intelligence?.phoneNumbers?.join(', ') || 'None'}</p>
              <p>Links: {sessionData.intelligence?.phishingLinks?.join(', ') || 'None'}</p>
              
              <p className="text-gray-400 mt-4"># AGENT NOTES</p>
              {sessionData.agent_notes?.map((note, idx) => (
                <p key={idx} className="text-blue-300">- {note}</p>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 italic">Awaiting data extraction...</p>
          )}
        </div>
      </div>

      {/* CENTER PANE - Chat Interface */}
      <div className="w-2/4 flex flex-col bg-gray-800">
        <div className="p-4 bg-gray-900 border-b border-gray-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></div>
            <h2 className="font-semibold text-lg">Scammer Simulation UI</h2>
          </div>
          <div className="flex items-center gap-3">
            <button 
              onClick={endChat}
              className="flex items-center gap-1 text-xs bg-red-900/50 hover:bg-red-800 text-red-200 px-2 py-1 rounded transition-colors border border-red-800/50"
            >
              <Trash2 size={14} /> End Chat
            </button>
            <div className="text-xs text-gray-400 bg-gray-700 px-2 py-1 rounded">
              Target: Honeypot Agent
            </div>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-gray-500">
              <Server size={48} className="mb-4 opacity-50" />
              <p>Start messaging the honeypot to begin the simulation.</p>
              <p className="text-sm mt-2">You are playing the role of the scammer.</p>
            </div>
          )}
          
          {messages.map((msg, index) => (
            <div key={index} className={`flex flex-col ${msg.sender === 'scammer' ? 'items-end' : 'items-start'}`}>
              <div 
                className={`max-w-[80%] p-3 rounded-lg ${
                  msg.sender === 'scammer' 
                    ? 'bg-blue-600 text-white rounded-tr-none' 
                    : msg.sender === 'system'
                    ? 'bg-red-900/50 text-red-200 border border-red-700 w-full text-center'
                    : 'bg-gray-700 text-gray-100 rounded-tl-none border border-gray-600'
                }`}
              >
                {msg.sender === 'system' ? (
                  <div className="flex items-center justify-center gap-2">
                    <AlertCircle size={16} />
                    <span>{msg.text}</span>
                  </div>
                ) : (
                  <p>{msg.text}</p>
                )}
              </div>
              <span className="text-xs text-gray-500 mt-1">
                {msg.sender === 'scammer' ? 'You (Scammer)' : msg.sender === 'user' ? 'Victim (Honeypot)' : 'System'} • {formatTime(msg.timestamp)}
              </span>
            </div>
          ))}
          
          {isTyping && (
            <div className="flex items-start">
              <div className="bg-gray-700 p-4 rounded-lg rounded-tl-none border border-gray-600">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 bg-gray-900 border-t border-gray-700">
          <form onSubmit={sendMessage} className="flex gap-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type your scam message here..."
              className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500 text-white"
              disabled={isTyping}
            />
            <button
              type="submit"
              disabled={isTyping || !inputValue.trim()}
              className="bg-blue-600 hover:bg-blue-700 text-white p-2 px-4 rounded-lg flex items-center justify-center disabled:opacity-50 transition-colors"
            >
              <Send size={20} />
            </button>
          </form>
        </div>
      </div>

      {/* RIGHT PANE - System Logs */}
      <div className="w-1/4 border-l border-gray-700 bg-black flex flex-col">
        <div className="p-4 bg-gray-900 border-b border-gray-700 flex items-center gap-2">
          <Activity size={20} className="text-yellow-400" />
          <h2 className="font-semibold text-lg">Active Logs</h2>
        </div>
        <div className="p-4 flex-1 overflow-y-auto font-mono text-xs text-gray-300 space-y-2">
          {logs.map((log, index) => (
            <div key={index} className="border-b border-gray-800 pb-2">
              <span className="text-gray-600 block">{formatTime(log.time)}</span>
              <span className={
                log.message.includes('Error') || log.message.includes('Failed') ? 'text-red-400' :
                log.message.includes('Connected') || log.message.includes('successfully') ? 'text-green-400' :
                'text-yellow-100'
              }>
                {log.message}
              </span>
            </div>
          ))}
          <div ref={logsEndRef} />
        </div>
      </div>

    </div>
  );
}

export default App;
