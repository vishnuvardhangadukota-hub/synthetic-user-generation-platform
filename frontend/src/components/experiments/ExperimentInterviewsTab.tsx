import React, { useState, useEffect, useRef } from 'react';
import {
  MessagesSquare,
  Send,
  User,
  Sparkles,
  Brain,
  History,
  RotateCcw,
  CheckCircle2,
} from 'lucide-react';
import { conversationsApi } from '@/services/api';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';
import { useToast } from '@/context/ToastContext';
import type { Persona, PersonaFullMemoryResponse, ConversationHistoryItem } from '@/types';

interface ExperimentInterviewsTabProps {
  personas: Persona[];
  initialSelectedPersona?: Persona | null;
  onRefreshParent: () => void;
}

interface ChatMessage {
  id: string;
  sender: 'user' | 'persona';
  text: string;
  timestamp: string;
}

export const ExperimentInterviewsTab: React.FC<ExperimentInterviewsTabProps> = ({
  personas,
  initialSelectedPersona,
  onRefreshParent,
}) => {
  const { success, error } = useToast();

  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(
    initialSelectedPersona || (personas.length > 0 ? personas[0] : null)
  );
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);

  // Live memory inspection
  const [memoryData, setMemoryData] = useState<PersonaFullMemoryResponse | null>(null);
  const [isLoadingMemory, setIsLoadingMemory] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Update selected persona if initialSelectedPersona changes from outside
  useEffect(() => {
    if (initialSelectedPersona) {
      setSelectedPersona(initialSelectedPersona);
    } else if (!selectedPersona && personas.length > 0) {
      setSelectedPersona(personas[0]);
    }
  }, [initialSelectedPersona, personas]);

  // When selected persona changes, load its conversation history and memory
  useEffect(() => {
    if (!selectedPersona) {
      setMessages([]);
      setMemoryData(null);
      return;
    }

    const loadHistoryAndMemory = async () => {
      try {
        setIsLoadingMemory(true);
        const mem = await conversationsApi.getMemory(selectedPersona.id);
        setMemoryData(mem);

        // Populate chat messages from persona history
        if (mem.conversation_history && mem.conversation_history.length > 0) {
          const loadedMessages: ChatMessage[] = [];
          mem.conversation_history.forEach((h: ConversationHistoryItem) => {
            loadedMessages.push({
              id: `${h.id}_user`,
              sender: 'user',
              text: h.user_message,
              timestamp: h.created_at,
            });
            loadedMessages.push({
              id: `${h.id}_persona`,
              sender: 'persona',
              text: h.persona_response,
              timestamp: h.created_at,
            });
          });
          setMessages(loadedMessages);
        } else {
          setMessages([
            {
              id: 'init_welcome',
              sender: 'persona',
              text: `Hello! I'm ${selectedPersona.name}, working as a ${selectedPersona.occupation} in ${selectedPersona.location}. What would you like to ask me about your product?`,
              timestamp: new Date().toISOString(),
            },
          ]);
        }
      } catch (err: any) {
        error('Failed to load memory', err.message);
      } finally {
        setIsLoadingMemory(false);
      }
    };

    loadHistoryAndMemory();
  }, [selectedPersona?.id]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || !selectedPersona || isSending) return;

    const userText = inputValue.trim();
    setInputValue('');

    const userMsg: ChatMessage = {
      id: `msg_u_${Date.now()}`,
      sender: 'user',
      text: userText,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      setIsSending(true);
      const res = await conversationsApi.sendMessage(selectedPersona.id, userText);

      const personaMsg: ChatMessage = {
        id: `msg_p_${Date.now()}`,
        sender: 'persona',
        text: res.response,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, personaMsg]);

      // Re-fetch memory to show real-time memory evolution
      if (res.memory_updated) {
        const updatedMem = await conversationsApi.getMemory(selectedPersona.id);
        setMemoryData(updatedMem);
      }
      onRefreshParent();
    } catch (err: any) {
      error('Message failed', err.message);
    } finally {
      setIsSending(false);
    }
  };

  const suggestedQuestions = [
    'What is your biggest frustration with existing products in this category?',
    'How would this product fit into your daily budget and routine?',
    'What feature would convince you to switch immediately?',
  ];

  if (personas.length === 0) {
    return (
      <EmptyState
        icon={<MessagesSquare className="w-6 h-6 text-indigo-600" />}
        title="No personas available for interview"
        description="Please generate synthetic personas first before conducting 1-on-1 interview simulations."
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Persona Selector Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-3.5 rounded-xl border border-slate-200/80 shadow-xs">
        <div className="flex items-center gap-3">
          <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider shrink-0">
            Interviewing Persona:
          </label>
          <select
            value={selectedPersona?.id || ''}
            onChange={(e) => {
              const p = personas.find((x) => x.id === e.target.value);
              if (p) setSelectedPersona(p);
            }}
            className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs sm:text-sm font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
          >
            {personas.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.occupation}, {p.age} yrs)
              </option>
            ))}
          </select>
        </div>

        {selectedPersona && (
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="font-medium text-slate-700">Memory Consistent Agent</span>
          </div>
        )}
      </div>

      {/* Main Split: Interactive Chat & Live Memory Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat Window (2 Cols) */}
        <div className="lg:col-span-2">
          <Card className="flex flex-col h-[600px] overflow-hidden">
            <CardHeader className="py-3 px-5 bg-slate-50/50">
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-xs">
                    {selectedPersona?.name.charAt(0)}
                  </div>
                  <div>
                    <CardTitle className="text-sm font-bold text-slate-900">
                      {selectedPersona?.name}
                    </CardTitle>
                    <CardDescription className="text-[11px]">
                      {selectedPersona?.occupation} &bull; {selectedPersona?.location}
                    </CardDescription>
                  </div>
                </div>

                <Badge variant="purple" size="sm">
                  Active Session
                </Badge>
              </div>
            </CardHeader>

            {/* Messages Feed */}
            <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-3.5 bg-slate-50/20">
              {messages.map((msg) => {
                const isUser = msg.sender === 'user';
                return (
                  <div
                    key={msg.id}
                    className={`flex items-start gap-2.5 ${isUser ? 'flex-row-reverse' : ''}`}
                  >
                    {!isUser && (
                      <div className="w-7 h-7 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs shrink-0 shadow-xs">
                        {selectedPersona?.name.charAt(0)}
                      </div>
                    )}
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-xs sm:text-sm leading-relaxed shadow-xs ${
                        isUser
                          ? 'bg-indigo-600 text-white rounded-tr-none'
                          : 'bg-white text-slate-800 border border-slate-200/80 rounded-tl-none'
                      }`}
                    >
                      <p>{msg.text}</p>
                      <span
                        className={`text-[10px] mt-1 block font-mono ${
                          isUser ? 'text-indigo-200 text-right' : 'text-slate-400'
                        }`}
                      >
                        {new Date(msg.timestamp).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </span>
                    </div>
                  </div>
                );
              })}
              {isSending && (
                <div className="flex items-center gap-2 text-xs text-slate-400 italic py-1">
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
                  {selectedPersona?.name} is thinking...
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Quick suggested prompts */}
            <div className="px-4 py-2 bg-slate-50/80 border-t border-slate-100 flex items-center gap-2 overflow-x-auto text-[11px] scrollbar-none">
              <span className="font-semibold text-slate-400 shrink-0">Prompts:</span>
              {suggestedQuestions.map((q, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setInputValue(q)}
                  className="px-2.5 py-1 rounded-full bg-white border border-slate-200 text-slate-600 hover:text-indigo-600 hover:border-indigo-200 transition-colors shrink-0 truncate max-w-xs"
                >
                  {q}
                </button>
              ))}
            </div>

            {/* Input Bar */}
            <form onSubmit={handleSendMessage} className="p-3 bg-white border-t border-slate-100 flex items-center gap-2">
              <input
                type="text"
                placeholder={`Ask ${selectedPersona?.name || 'persona'} a question...`}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                disabled={isSending}
                className="flex-1 rounded-lg border border-slate-200 px-3.5 py-2 text-xs sm:text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600"
              />
              <Button
                type="submit"
                variant="primary"
                size="md"
                isLoading={isSending}
                leftIcon={<Send className="w-3.5 h-3.5" />}
              >
                Send
              </Button>
            </form>
          </Card>
        </div>

        {/* Live Memory Inspector (1 Col) */}
        <div className="lg:col-span-1">
          <Card className="h-[600px] flex flex-col">
            <CardHeader className="py-3 px-5 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <Brain className="w-4 h-4 text-indigo-600" />
                <CardTitle className="text-sm">Persona Memory State</CardTitle>
              </div>
              <CardDescription className="text-[11px]">
                Real-time partition of persona consistency memory
              </CardDescription>
            </CardHeader>

            <CardContent className="p-4 flex-1 overflow-y-auto space-y-4 text-xs">
              {/* Core Attributes */}
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block mb-1.5">
                  1. Core Memory (Permanent)
                </span>
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-150 space-y-1 text-slate-700">
                  <p>
                    <strong className="text-slate-900">Name:</strong> {selectedPersona?.name}
                  </p>
                  <p>
                    <strong className="text-slate-900">Age:</strong> {selectedPersona?.age}
                  </p>
                  <p>
                    <strong className="text-slate-900">Job:</strong> {selectedPersona?.occupation}
                  </p>
                  <p>
                    <strong className="text-slate-900">Decision Style:</strong>{' '}
                    {selectedPersona?.psychological_profile?.decision_style || 'Balanced'}
                  </p>
                </div>
              </div>

              {/* Established Opinions */}
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block mb-1.5">
                  2. Opinion Memory (Prevents Contradiction)
                </span>
                {memoryData?.opinions && memoryData.opinions.length > 0 ? (
                  <div className="space-y-1.5">
                    {memoryData.opinions.map((op, idx) => (
                      <div
                        key={idx}
                        className="p-2.5 rounded-lg bg-violet-50/60 border border-violet-100 text-violet-900"
                      >
                        <p className="font-semibold text-[11px]">{op.topic || 'General'}:</p>
                        <p className="mt-0.5 text-xs text-violet-800">{op.content || op.opinion}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-3 rounded-lg border border-dashed border-slate-200 text-slate-400 text-center text-[11px]">
                    No opinions formed yet. Opinions crystallize during chat.
                  </div>
                )}
              </div>

              {/* Behavioral Memories */}
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block mb-1.5">
                  3. Behavioral Memory (Habits & Routine)
                </span>
                {memoryData?.behavioral_memories && memoryData.behavioral_memories.length > 0 ? (
                  <div className="space-y-1.5">
                    {memoryData.behavioral_memories.map((bm, idx) => (
                      <div
                        key={idx}
                        className="p-2.5 rounded-lg bg-indigo-50/60 border border-indigo-100 text-indigo-900 text-xs"
                      >
                        {bm.content || bm.behavior}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-3 rounded-lg border border-dashed border-slate-200 text-slate-400 text-center text-[11px]">
                    Default habits applied.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
