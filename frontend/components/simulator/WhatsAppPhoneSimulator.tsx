"use client";

import React, { useReducer, useState, useEffect, useRef } from "react";
import { Send, Phone, Video, MoreVertical, CheckCircle2, RotateCcw } from "lucide-react";
import { conversationReducer, type ConversationState } from "./conversationMachine";
import { ChatBubble } from "./ChatBubble";
import { api } from "@/lib/api/client";

export interface WhatsAppPhoneSimulatorProps {
  orderId?: string;
  customerName?: string;
  streetAddress?: string;
  addressQuality?: "Complete" | "NeedsLandmark" | "Poor";
  onOrderUpdated?: () => void;
}

const initialState: ConversationState = {
  step: "INIT",
  messages: [],
  orderId: "ORD-20261128-DEMO",
  customerName: "Priya Sharma",
  streetAddress: "House 12, Sector 15",
  addressQuality: "NeedsLandmark",
  landmark: null,
  deliverySlot: null,
  isTyping: false,
};

export function WhatsAppPhoneSimulator({
  orderId = "ORD-20261128-DEMO",
  customerName = "Priya Sharma",
  streetAddress = "House 12, Sector 15",
  addressQuality = "NeedsLandmark",
  onOrderUpdated,
}: WhatsAppPhoneSimulatorProps) {
  const [state, dispatch] = useReducer(conversationReducer, {
    ...initialState,
    orderId,
    customerName,
    streetAddress,
    addressQuality,
  });

  const [inputText, setInputText] = useState("");
  const [syncStatus, setSyncStatus] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom of chat
  const scrollToBottom = () => {
    if (typeof messagesEndRef.current?.scrollIntoView === "function") {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [state.messages, state.isTyping]);

  // Initial startup message
  useEffect(() => {
    dispatch({
      type: "START_CONVERSATION",
      orderId,
      customerName,
      address: streetAddress,
      quality: addressQuality,
    });
  }, [orderId, customerName, streetAddress, addressQuality]);

  // Handle bot replies based on user message and current step
  const handleUserReply = (text: string) => {
    dispatch({ type: "SEND_USER_MESSAGE", text });

    const trimmed = text.trim();

    // 1. Opt-out handling
    if (trimmed.toUpperCase() === "STOP") {
      setTimeout(() => {
        dispatch({
          type: "RECEIVE_BOT_MESSAGE",
          text: "You have unsubscribed from ReturnZero WhatsApp updates. No further messages will be sent.",
          nextStep: "OPTED_OUT",
        });
        // Call backend verify with opt_out
        api.verifyOrder(state.orderId, { opt_in_whatsapp: false }).catch(() => null);
      }, 700);
      return;
    }

    // 2. Consent flow
    if (state.step === "CONSENT_PROMPT") {
      setTimeout(() => {
        if (state.addressQuality === "NeedsLandmark" || state.addressQuality === "Poor") {
          dispatch({
            type: "RECEIVE_BOT_MESSAGE",
            text: `Great! We noticed your address '${state.streetAddress}' doesn't include a prominent landmark. Could you reply with a nearby landmark (e.g. Near Metro Pillar, opposite park) to assist the delivery rider?`,
            quickReplies: ["Near Metro Pillar 120", "Opposite City Hospital", "Behind Mother Dairy"],
            nextStep: "AWAITING_LANDMARK",
          });
        } else {
          dispatch({
            type: "RECEIVE_BOT_MESSAGE",
            text: "Great! Your delivery address is complete. Please choose your preferred delivery time slot:",
            quickReplies: ["Morning (9 AM - 1 PM)", "Afternoon (2 PM - 6 PM)", "Evening (6 PM - 9 PM)"],
            nextStep: "SLOT_SELECTION",
          });
        }
      }, 800);
      return;
    }

    // 3. Landmark input flow
    if (state.step === "AWAITING_LANDMARK") {
      setTimeout(() => {
        dispatch({
          type: "RECEIVE_BOT_MESSAGE",
          text: `Thank you! Landmark noted: "${trimmed}". Now, please pick your preferred delivery time window:`,
          quickReplies: ["Morning (9 AM - 1 PM)", "Afternoon (2 PM - 6 PM)", "Evening (6 PM - 9 PM)"],
          nextStep: "SLOT_SELECTION",
        });
      }, 800);
      return;
    }

    // 4. Slot selection flow -> Safe_For_Dispatch
    if (state.step === "SLOT_SELECTION") {
      setTimeout(async () => {
        const confirmedMsg = `✅ All set! Your delivery slot is locked for ${trimmed}. We've updated your instructions for the courier. Your order is now Safe for Dispatch!`;
        dispatch({
          type: "RECEIVE_BOT_MESSAGE",
          text: confirmedMsg,
          nextStep: "SAFE_FOR_DISPATCH",
        });

        // Sync with backend API (never fabricate dummy landmark)
        try {
          await api.verifyOrder(state.orderId, {
            landmark: state.landmark ? state.landmark : undefined,
            delivery_slot: trimmed,
            opt_in_whatsapp: true,
          });
          setSyncStatus(`[Database Synced] Order #${state.orderId} marked 'Safe_For_Dispatch'`);
          onOrderUpdated?.();
        } catch {
          setSyncStatus(`[Local Simulated] Order #${state.orderId} marked 'Safe_For_Dispatch'`);
        }
      }, 800);
      return;
    }

    // 5. NDR Reschedule flow
    if (state.step === "NDR_ALERT") {
      setTimeout(async () => {
        dispatch({
          type: "RECEIVE_BOT_MESSAGE",
          text: `✅ Reattempt confirmed! Courier will re-deliver tomorrow during ${trimmed}. Thank you for confirming!`,
          nextStep: "NDR_RESCHEDULED",
        });

        try {
          await api.rescheduleNdr(state.orderId, {
            reschedule_date: "Tomorrow",
            reschedule_slot: trimmed,
          });
          setSyncStatus(`[Database Synced] Order #${state.orderId} marked 'Delivery_Rescheduled'`);
          onOrderUpdated?.();
        } catch {
          setSyncStatus(`[Local Simulated] Order #${state.orderId} marked 'Delivery_Rescheduled'`);
        }
      }, 800);
    }
  };

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || state.step === "OPTED_OUT") return;
    handleUserReply(inputText);
    setInputText("");
  };

  const triggerNdr = () => {
    dispatch({ type: "TRIGGER_NDR_SIMULATION" });
  };

  return (
    <div className="flex flex-col items-center justify-center p-2 sm:p-4">
      {/* Sticky Top Ribbon (ADR-015) */}
      <div className="w-full max-w-[360px] bg-amber-500 text-white text-[11px] font-bold py-1 px-3 text-center rounded-t-xl tracking-wide shadow-sm flex items-center justify-center gap-1.5">
        <span>⚡ Simulated — no real WhatsApp message is sent</span>
      </div>

      {/* iPhone 15 Frame */}
      <div className="w-[360px] h-[640px] bg-[#E5DDD5] rounded-b-[40px] border-4 border-gray-900 shadow-2xl overflow-hidden flex flex-col relative">
        {/* Dynamic Island / Notch */}
        <div className="w-full bg-[#075E54] pt-2 px-6 pb-1 flex justify-between items-center text-white text-[11px] font-semibold select-none">
          <span>9:41</span>
          <div className="w-20 h-4 bg-black rounded-full" />
          <div className="flex items-center gap-1">
            <span className="text-[10px]">5G</span>
            <div className="w-4 h-2 border border-white rounded-xs flex items-center p-0.5">
              <div className="w-full h-full bg-white rounded-xs" />
            </div>
          </div>
        </div>

        {/* WhatsApp App Header */}
        <div className="bg-[#075E54] text-white px-3 py-2.5 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-full bg-white text-[#075E54] flex items-center justify-center font-bold text-xs shadow-xs">
              RZ
            </div>
            <div>
              <div className="font-bold text-xs flex items-center gap-1 leading-tight">
                ReturnZero Delivery
                <CheckCircle2 className="w-3.5 h-3.5 text-[#25D366] fill-[#25D366]" />
              </div>
              <div className="text-[10px] text-emerald-200">
                {state.isTyping ? "typing..." : "Verified Official Bot"}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3 text-white">
            <Video className="w-4 h-4 opacity-80" />
            <Phone className="w-4 h-4 opacity-80" />
            <MoreVertical className="w-4 h-4 opacity-80" />
          </div>
        </div>

        {/* Chat Feed */}
        <div className="flex-1 overflow-y-auto p-3 space-y-2.5 bg-[radial-gradient(#d3c8be_1px,transparent_1px)] [background-size:16px_16px]">
          {state.messages.map((msg) => (
            <ChatBubble key={msg.id} message={msg} onQuickReply={handleUserReply} />
          ))}

          {/* Typing Indicator */}
          {state.isTyping && (
            <div className="flex items-center gap-1 bg-white px-3 py-2 rounded-2xl w-14 shadow-sm">
              <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" />
              <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]" />
              <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:0.4s]" />
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Bottom Input Field */}
        <form onSubmit={handleSend} className="bg-[#F0F2F5] p-2 flex items-center gap-1.5 border-t border-gray-200">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={state.step === "OPTED_OUT"}
            placeholder={state.step === "OPTED_OUT" ? "Unsubscribed (STOP)" : "Type a message..."}
            className="flex-1 bg-white text-xs px-3.5 py-2 rounded-full border border-gray-300 focus:outline-none focus:border-[#00A884]"
          />
          <button
            type="submit"
            disabled={!inputText.trim() || state.step === "OPTED_OUT"}
            className="w-8 h-8 rounded-full bg-[#00A884] text-white flex items-center justify-center hover:bg-[#008f6f] disabled:opacity-40 transition-colors shadow-sm"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>

      {/* Simulator Control & DB Sync Toast */}
      <div className="w-full max-w-[360px] mt-3 space-y-2 text-center">
        {syncStatus && (
          <div className="p-2 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-bold animate-in fade-in">
            {syncStatus}
          </div>
        )}
        <div className="flex gap-2 justify-center">
          <button
            type="button"
            onClick={triggerNdr}
            className="text-[11px] font-semibold text-rose-700 hover:text-rose-900 bg-rose-50 hover:bg-rose-100 border border-rose-200 px-3 py-1 rounded-full transition-colors inline-flex items-center gap-1"
          >
            <RotateCcw className="w-3 h-3" />
            Simulate Courier NDR Failure
          </button>
        </div>
      </div>
    </div>
  );
}
