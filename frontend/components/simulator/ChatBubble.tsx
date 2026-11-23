import React from "react";
import { CheckCheck } from "lucide-react";
import type { ChatMessage } from "./conversationMachine";
import { cn } from "@/lib/cn";

export interface ChatBubbleProps {
  message: ChatMessage;
  onQuickReply?: (reply: string) => void;
}

export function ChatBubble({ message, onQuickReply }: ChatBubbleProps) {
  const isBot = message.sender === "bot";

  return (
    <div className={cn("flex flex-col space-y-1.5", isBot ? "items-start" : "items-end")}>
      <div
        className={cn(
          "max-w-[85%] rounded-2xl px-3.5 py-2 text-xs leading-relaxed shadow-sm relative",
          isBot
            ? "bg-white text-ink border border-gray-100 rounded-tl-sm"
            : "bg-[#DCF8C6] text-ink rounded-tr-sm",
        )}
      >
        <p className="whitespace-pre-line">{message.text}</p>
        <div className="flex items-center justify-end gap-1 text-[9px] text-gray-500 mt-1">
          <span>{message.timestamp}</span>
          {!isBot && <CheckCheck className="w-3 h-3 text-[#34B7F1]" />}
        </div>
      </div>

      {/* Quick Reply Chips */}
      {isBot && message.quickReplies && message.quickReplies.length > 0 && (
        <div className="flex flex-wrap gap-1.5 max-w-[90%] mt-1">
          {message.quickReplies.map((reply) => (
            <button
              key={reply}
              type="button"
              onClick={() => onQuickReply?.(reply)}
              className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-white text-[#00A884] border border-[#00A884]/40 hover:bg-[#00A884]/10 transition-colors shadow-xs"
            >
              {reply}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
