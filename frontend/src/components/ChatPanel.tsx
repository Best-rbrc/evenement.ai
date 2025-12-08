import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { MessageSquare, Send, Loader2, Bot, User, Sparkles, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';
import { EventPlanResult } from '@/types/event';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface ChatMessage {
  id: string;
  role: 'user' | 'coordinator';
  content: string;
  timestamp: Date;
  agentsCalled?: string[];
  changedSections?: string[];
}

interface ChatPanelProps {
  currentPlan: EventPlanResult;
  originalWorkflowResult: any; // The full workflow result from backend
  onPlanUpdate: (updatedPlan: EventPlanResult) => void;
}

export function ChatPanel({ currentPlan, originalWorkflowResult, onPlanUpdate }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Prepare request payload
      const requestPayload = {
        message: userMessage.content,
        current_plan: originalWorkflowResult?.result?.final_plan || {},
        specialist_outputs: originalWorkflowResult?.result?.specialist_outputs || {},
        event_details: originalWorkflowResult?.result?.event_details || originalWorkflowResult?.event_details || {},
        required_agents: originalWorkflowResult?.result?.agents_used || [],
      };

      const response = await fetch(`${API_BASE_URL}/api/refine-plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestPayload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const data = await response.json();

      // Add coordinator response
      const coordinatorMessage: ChatMessage = {
        id: `coordinator-${Date.now()}`,
        role: 'coordinator',
        content: data.coordinator_message || 'Plan updated successfully',
        timestamp: new Date(),
        agentsCalled: data.agents_called || [],
        changedSections: data.changed_sections || [],
      };

      setMessages((prev) => [...prev, coordinatorMessage]);

      // Update the plan if we got an updated plan
      if (data.updated_plan) {
        // Update the original workflow result with new plan
        const updatedWorkflowResult = {
          ...originalWorkflowResult,
          result: {
            ...originalWorkflowResult.result,
            final_plan: data.updated_plan,
            // Merge updated specialist outputs
            specialist_outputs: {
              ...originalWorkflowResult.result.specialist_outputs,
              ...(data.specialist_outputs || {}),
            },
          },
        };

        toast({
          title: 'Plan Updated',
          description: `Updated ${data.changed_sections?.join(', ') || 'plan'} based on your request.`,
        });

        // Notify parent of update - parent will remap to EventPlanResult
        onPlanUpdate(updatedWorkflowResult);
      }

      if (data.error) {
        toast({
          title: 'Refinement Error',
          description: data.error,
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        role: 'coordinator',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to process your request',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Floating Chat Button - positioned to the left of DevMenu */}
      <Button
        variant="outline"
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-24 z-50 w-14 h-14 rounded-full shadow-lg hover:shadow-xl transition-shadow"
        size="icon"
        title={isOpen ? "Close chat" : "Chat with coordinator"}
      >
        {isOpen ? <X className="w-5 h-5" /> : <MessageSquare className="w-5 h-5" />}
      </Button>

      {/* Chat Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="fixed bottom-24 right-28 z-50 w-96 max-h-[600px]"
          >
            <Card className="shadow-2xl border-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5" />
                  Chat with Coordinator
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                {/* Messages */}
                <ScrollArea className="h-[400px] p-4" ref={scrollAreaRef}>
                  <div className="space-y-4">
                    {messages.length === 0 && (
                      <div className="text-center text-muted-foreground py-8">
                        <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>Ask me to make changes to your event plan!</p>
                        <p className="text-sm mt-2">Try: "Change the venue to something cheaper"</p>
                      </div>
                    )}
                    {messages.map((message) => (
                      <motion.div
                        key={message.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className={cn(
                          'flex gap-3',
                          message.role === 'user' ? 'justify-end' : 'justify-start'
                        )}
                      >
                        {message.role === 'coordinator' && (
                          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                            <Bot className="h-4 w-4 text-primary" />
                          </div>
                        )}
                        <div
                          className={cn(
                            'max-w-[80%] rounded-lg p-3',
                            message.role === 'user'
                              ? 'bg-primary text-primary-foreground'
                              : 'bg-muted'
                          )}
                        >
                          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                          {(message.agentsCalled?.length || message.changedSections?.length) && (
                            <div className="mt-2 flex flex-wrap gap-1">
                              {message.changedSections?.map((section) => (
                                <Badge key={section} variant="secondary" className="text-xs">
                                  {section}
                                </Badge>
                              ))}
                            </div>
                          )}
                          <p className="text-xs opacity-70 mt-1">
                            {message.timestamp.toLocaleTimeString()}
                          </p>
                        </div>
                        {message.role === 'user' && (
                          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                            <User className="h-4 w-4 text-primary" />
                          </div>
                        )}
                      </motion.div>
                    ))}
                    {isLoading && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex gap-3 justify-start"
                      >
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                          <Bot className="h-4 w-4 text-primary" />
                        </div>
                        <div className="bg-muted rounded-lg p-3">
                          <div className="flex items-center gap-2">
                            <Loader2 className="h-4 w-4 animate-spin" />
                            <p className="text-sm text-muted-foreground">Coordinator is working...</p>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </div>
                </ScrollArea>

                {/* Input */}
                <div className="border-t p-4">
                  <div className="flex gap-2">
                    <Input
                      ref={inputRef}
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Ask for changes to your plan..."
                      disabled={isLoading}
                      className="flex-1"
                    />
                    <Button
                      onClick={handleSend}
                      disabled={!inputValue.trim() || isLoading}
                      size="icon"
                    >
                      {isLoading ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Send className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

