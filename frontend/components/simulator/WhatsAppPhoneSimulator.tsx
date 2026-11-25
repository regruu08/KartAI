"use client";

import React, { useReducer, useState, useEffect, useRef } from "react";
import {
  Send,
  Phone,
  Video,
  MoreVertical,
  BadgeCheck,
  RotateCcw,
  Signal,
  Wifi,
  BatteryFull,
} from "lucide-react";
import { conversationReducer, type ConversationState } from "./conversationMachine";
import { ChatBubble } from "./ChatBubble";
import { api } from "@/lib/api/client";

export interface WhatsAppSyncActivity {
  endpoint: string;
  requestPayload: unknown;
  responsePayload?: unknown;
  step: string;
}

export interface WhatsAppPhoneSimulatorProps {
  orderId?: string;
  customerName?: string;
  streetAddress?: string;
  addressQuality?: "Complete" | "NeedsLandmark" | "Poor";
  onOrderUpdated?: () => void;
  onSyncActivity?: (activity: WhatsAppSyncActivity) => void;
}

const initialState: ConversationState = {
  step: "INIT",
  messages: [],
  orderId: "RZ-1042",
  customerName: "Priya Sharma",
  streetAddress: "House 12, Sector 15",
  addressQuality: "NeedsLandmark",
  landmark: null,
  deliverySlot: null,
  isTyping: false,
};

export function WhatsAppPhoneSimulator({
  orderId = "RZ-1042",
  customerName = "Priya Sharma",
  streetAddress = "House 12, Sector 15",
  addressQuality = "NeedsLandmark",
  onOrderUpdated,
  onSyncActivity,
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

  const scrollToBottom = () => {
    if (typeof messagesEndRef.current?.scrollIntoView === "function") {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [state.messages, state.isTyping]);

  useEffect(() => {
    setSyncStatus(null);
    dispatch({
      type: "START_CONVERSATION",
      orderId,
      customerName,
      address: streetAddress,
      quality: addressQuality,
    });
  }, [orderId, customerName, streetAddress, addressQuality]);

  const handleUserReply = (text: string) => {
    dispatch({ type: "SEND_USER_MESSAGE", text });
    const trimmed = text.trim();

    // 1. STOP opt-out branch
    if (trimmed.toUpperCase() === "STOP") {
      setTimeout(async () => {
        dispatch({
          type: "RECEIVE_BOT_MESSAGE",
          text: "You have unsubscribed from ReturnZero WhatsApp updates. No further messages will be sent.",
          nextStep: "OPTED_OUT",
        });
        const payload = { opt_in_whatsapp: false };
        try {
          const res = await api.verifyOrder(state.orderId, payload);
          onSyncActivity?.({
            endpoint: `POST /v1/orders/${state.orderId}/verify`,
            requestPayload: payload,
            responsePayload: res,
            step: "OPTED_OUT",
          });
          setSyncStatus(`Order #${state.orderId} marked 'opted_out'`);
          onOrderUpdated?.();
        } catch {
          onSyncActivity?.({
            endpoint: `POST /v1/orders/${state.orderId}/verify`,
            requestPayload: payload,
            responsePayload: { consent_status: "opted_out", simulated: true },
            step: "OPTED_OUT",
          });
        }
      }, 600);
      return;
    }

    // 2. Consent opt-in flow
    if (state.step === "CONSENT_PROMPT") {
      setTimeout(() => {
        if (state.addressQuality === "NeedsLandmark" || state.addressQuality === "Poor") {
          dispatch({
            type: "RECEIVE_BOT_MESSAGE",
            text: `Great! We noticed your address '${state.streetAddress}' doesn't include a prominent landmark. Could you reply with a nearby landmark (e.g. Near Metro Pillar, opposite park) to assist the delivery rider?`,
            quickReplies: ["Near Metro Pillar 120", "Opposite City Hospital", "Behind Mother Dairy"],
            nextStep: "AWAITING_LANDMARK",
          });
          onSyncActivity?.({
            endpoint: `POST /v1/orders/${state.orderId}/verify`,
            requestPayload: { opt_in_whatsapp: true },
            step: "AWAITING_LANDMARK",
          });
        } else {
          dispatch({
            type: "RECEIVE_BOT_MESSAGE",
            text: "Great! Your delivery address is complete. Please choose your preferred delivery time slot:",
            quickReplies: [
              "Morning (9 AM - 1 PM)",
              "Afternoon (2 PM - 6 PM)",
              "Evening (6 PM - 9 PM)",
            ],
            nextStep: "SLOT_SELECTION",
          });
          onSyncActivity?.({
            endpoint: `POST /v1/orders/${state.orderId}/verify`,
            requestPayload: { opt_in_whatsapp: true },
            step: "SLOT_SELECTION",
          });
        }
      }, 650);
      return;
    }

    // 3. Landmark clarification
    if (state.step === "AWAITING_LANDMARK") {
      setTimeout(() => {
        dispatch({
          type: "RECEIVE_BOT_MESSAGE",
          text: `Thank you! Landmark noted: "${trimmed}". Now, please pick your preferred delivery time window:`,
          quickReplies: [
            "Morning (9 AM - 1 PM)",
            "Afternoon (2 PM - 6 PM)",
            "Evening (6 PM - 9 PM)",
          ],
          nextStep: "SLOT_SELECTION",
        });
        onSyncActivity?.({
          endpoint: `POST /v1/orders/${state.orderId}/verify`,
          requestPayload: { landmark: trimmed, opt_in_whatsapp: true },
          step: "SLOT_SELECTION",
        });
      }, 650);
      return;
    }

    // 4. Slot selection -> Safe_For_Dispatch
    if (state.step === "SLOT_SELECTION") {
      setTimeout(async () => {
        dispatch({
          type: "RECEIVE_BOT_MESSAGE",
          text: `All set! Your delivery slot is locked for ${trimmed}. We've updated your instructions for the courier. Your order is now Safe for Dispatch!`,
          nextStep: "SAFE_FOR_DISPATCH",
        });

        const payload = {
          landmark: state.landmark ? state.landmark : undefined,
          delivery_slot: trimmed,
          opt_in_whatsapp: true,
        };
        try {
          const res = await api.verifyOrder(state.orderId, payload);
          setSyncStatus(`[Database Synced] Order #${state.orderId} marked 'Safe_For_Dispatch'`);
          onSyncActivity?.({
            endpoint: `POST /v1/orders/${state.orderId}/verify`,
            requestPayload: payload,
            responsePayload: res,
            step: "SAFE_FOR_DISPATCH",
          });
          onOrderUpdated?.();
        } catch {
          setSyncStatus(`[Local Simulated] Order #${state.orderId} marked 'Safe_For_Dispatch'`);
          onSyncActivity?.({
            endpoint: `POST /v1/orders/${state.orderId}/verify`,
            requestPayload: payload,
            responsePayload: { order_status: "Safe_For_Dispatch", simulated: true },
            step: "SAFE_FOR_DISPATCH",
          });
        }
      }, 650);
      return;
    }

    // 5. NDR reschedule flow
    if (state.step === "NDR_ALERT") {
      setTimeout(async () => {
        dispatch({
          type: "RECEIVE_BOT_MESSAGE",
          text: `Reattempt confirmed! Courier will re-deliver tomorrow during ${trimmed}. Thank you for confirming!`,
          nextStep: "NDR_RESCHEDULED",
        });

        const payload = {
          reschedule_date: "Tomorrow",
          reschedule_slot: trimmed,
        };
        try {
          const res = await api.rescheduleNdr(state.orderId, payload);
          setSyncStatus(
            `[Database Synced] Order #${state.orderId} marked 'Delivery_Rescheduled'`,
          );
          onSyncActivity?.({
            endpoint: `POST /v1/orders/${state.orderId}/ndr`,
            requestPayload: payload,
            responsePayload: res,
            step: "NDR_RESCHEDULED",
          });
          onOrderUpdated?.();
        } catch {
          setSyncStatus(
            `[Local Simulated] Order #${state.orderId} marked 'Delivery_Rescheduled'`,
          );
          onSyncActivity?.({
            endpoint: `POST /v1/orders/${state.orderId}/ndr`,
            requestPayload: payload,
            responsePayload: { order_status: "Delivery_Rescheduled", simulated: true },
            step: "NDR_RESCHEDULED",
          });
        }
      }, 650);
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
    onSyncActivity?.({
      endpoint: `Simulated NDR Trigger (${state.orderId})`,
      requestPayload: { event: "Courier_Attempt_Failed" },
      step: "NDR_ALERT",
    });
  };

  return (
    <div className="flex flex-col items-center justify-center w-full">
      {/* Honesty / Synthetic Notification Ribbon */}
      <div className="w-full max-w-[380px] bg-warn-soft border border-warn/35 text-warn-text text-[11px] font-semibold py-1.5 px-3 text-center rounded-t-2xl">
        Simulated — no real WhatsApp message is sent
      </div>

      {/* Smartphone Bezel Container */}
      <div className="w-full max-w-[380px] rounded-b-[42px] border-[9px] border-ink bg-ink shadow-lift overflow-hidden">
        <div className="rounded-b-[32px] bg-[#EFEAE2] flex flex-col h-[610px] sm:h-[650px]">
          {/* iOS Status Bar + Dynamic Island */}
          <div className="bg-[#075E54] text-white px-5 pt-2.5 pb-1.5 flex items-center justify-between text-[11px] font-semibold select-none">
            <span className="tabular-nums">9:41</span>
            <div className="h-4 w-20 rounded-full bg-black/85" aria-hidden="true" />
            <div className="flex items-center gap-1.5" aria-hidden="true">
              <Signal className="w-3 h-3" />
              <Wifi className="w-3 h-3" />
              <BatteryFull className="w-3.5 h-3.5" />
            </div>
          </div>

          {/* Official Business Header */}
          <div className="bg-[#075E54] text-white px-3.5 pb-2.5 pt-1 flex items-center justify-between border-b border-black/10">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="w-9 h-9 rounded-full bg-white/15 border border-white/25 text-white flex items-center justify-center font-display font-semibold text-xs shrink-0">
                RZ
              </div>
              <div className="min-w-0">
                <div className="font-semibold text-xs flex items-center gap-1 leading-tight">
                  <span className="truncate">ReturnZero Delivery</span>
                  <BadgeCheck className="w-3.5 h-3.5 text-[#25D366] shrink-0" aria-label="Verified" />
                </div>
                <div className="text-[10px] text-white/80">
                  {state.isTyping ? "typing…" : "online · Official Business Bot"}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2.5 text-white/85 shrink-0" aria-hidden="true">
              <Video className="w-4 h-4" />
              <Phone className="w-4 h-4" />
              <MoreVertical className="w-4 h-4" />
            </div>
          </div>

          {/* Chat Feed */}
          <div
            aria-live="polite"
            className="wa-wallpaper flex-1 overflow-y-auto p-3.5 space-y-2.5"
          >
            {state.messages.map((msg) => (
              <ChatBubble key={msg.id} message={msg} onQuickReply={handleUserReply} />
            ))}

            {state.isTyping && (
              <div
                aria-label="ReturnZero Delivery is typing"
                className="inline-flex items-center gap-1.5 bg-white px-3.5 py-2.5 rounded-2xl rounded-tl-sm shadow-sm"
              >
                <span className="rz-dot-1 h-1.5 w-1.5 rounded-full bg-ink-muted" />
                <span className="rz-dot-2 h-1.5 w-1.5 rounded-full bg-ink-muted" />
                <span className="rz-dot-3 h-1.5 w-1.5 rounded-full bg-ink-muted" />
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Interactive Message Input */}
          <form
            onSubmit={handleSend}
            className="bg-[#F0F2F5] p-2.5 flex items-center gap-2 border-t border-black/5"
          >
            <input
              type="text"
              aria-label="Reply in simulated WhatsApp chat"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              disabled={state.step === "OPTED_OUT"}
              placeholder={
                state.step === "OPTED_OUT"
                  ? "Unsubscribed (STOP)"
                  : "Type landmark or reply STOP..."
              }
              className="flex-1 bg-white text-xs text-ink px-3.5 py-2.5 rounded-full border border-gray-300 focus:outline-none focus:border-[#075E54]"
            />
            <button
              type="submit"
              aria-label="Send simulated WhatsApp reply"
              disabled={!inputText.trim() || state.step === "OPTED_OUT"}
              className="w-9 h-9 rounded-full bg-[#075E54] text-white flex items-center justify-center hover:bg-[#054a42] disabled:opacity-40 transition-colors shrink-0 cursor-pointer"
            >
              <Send className="w-3.5 h-3.5" aria-hidden="true" />
            </button>
          </form>
        </div>
      </div>

      {/* Live Sync Banner + Edge-Case NDR Trigger */}
      <div className="w-full max-w-[380px] mt-3 space-y-2 text-center">
        {syncStatus && (
          <div
            role="status"
            className="p-2.5 rounded-xl bg-trust-soft border border-trust/30 text-trust-text text-xs font-semibold"
          >
            {syncStatus}
          </div>
        )}
        <div className="flex justify-center">
          <button
            type="button"
            onClick={triggerNdr}
            className="text-xs font-semibold text-danger hover:bg-danger-soft bg-surface border border-danger/25 px-4 py-1.5 rounded-full transition-colors inline-flex items-center gap-1.5 cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Simulate Courier NDR Failure</span>
          </button>
        </div>
      </div>
    </div>
  );
}
