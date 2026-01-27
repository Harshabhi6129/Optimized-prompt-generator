"use client";

import { useState, useEffect, useRef } from "react";
import { Send, Loader2, Bot, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChatMessage } from "@/types";
import { generateId, formatDate } from "@/lib/utils";

interface ChatInterfaceProps {
  refinedPrompt?: string;
  onRefinedPromptUsed?: () => void;
}

export function ChatInterface({ refinedPrompt, onRefinedPromptUsed }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (refinedPrompt) {
      setInputMessage(refinedPrompt);
      textareaRef.current?.focus();
    }
  }, [refinedPrompt]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: generateId(),
      role: "user",
      content: inputMessage.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    if (refinedPrompt && inputMessage.trim() === refinedPrompt) {
      onRefinedPromptUsed?.();
    }

    try {
      const conversationHistory = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage.content,
          conversationHistory,
        }),
      });

      const data = await response.json();

      if (data.success) {
        const assistantMessage: ChatMessage = {
          id: generateId(),
          role: "model",
          content: data.response,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        const errorMessage: ChatMessage = {
          id: generateId(),
          role: "model",
          content: `Error: ${data.error || "Failed to get response"}`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage: ChatMessage = {
        id: generateId(),
        role: "model",
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <Card className="flex flex-col h-[600px]">
      <CardHeader className="border-b">
        <div className="flex items-center justify-between">
          <CardTitle>💬 Chat Interface</CardTitle>
          {isLoading && <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />}
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
            <Bot className="w-16 h-16 text-muted-foreground" />
            <div>
              <p className="text-lg font-medium">No messages yet. Start a conversation!</p>
              {refinedPrompt && (
                <p className="text-sm text-muted-foreground mt-2">
                  Your refined prompt is ready to use below.
                </p>
              )}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"
                  }`}
              >
                {message.role === "model" && (
                  <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center flex-shrink-0">
                    <Bot className="w-5 h-5" />
                  </div>
                )}
                <div
                  className={`max-w-[70%] rounded-lg p-3 ${message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-secondary"
                    }`}
                >
                  <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
                  <p
                    className={`text-xs mt-1 ${message.role === "user"
                        ? "text-primary-foreground/70"
                        : "text-muted-foreground"
                      }`}
                  >
                    {formatDate(message.timestamp)}
                  </p>
                </div>
                {message.role === "user" && (
                  <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                    <User className="w-5 h-5 text-primary-foreground" />
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </CardContent>

      <div className="border-t p-4 space-y-2">
        <div className="flex gap-2">
          <Textarea
            ref={textareaRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message... (Shift+Enter for new line)"
            disabled={isLoading}
            className="min-h-[60px] max-h-[200px] resize-none"
            rows={2}
          />
          <Button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            size="icon"
            className="w-[60px] h-[60px] flex-shrink-0"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </Button>
        </div>
        <p className="text-xs text-muted-foreground text-center">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </Card>
  );
}
