/** Pure conversational state machine for ReturnZero WhatsApp Delivery Assurance.
 *
 * Implements conversational flows for:
 * 1. Explicit consent opt-in & STOP opt-out (ADR-015)
 * 2. Address evaluation and landmark clarification
 * 3. Delivery slot selection
 * 4. Safe_For_Dispatch transition
 * 5. NDR (Non-Delivery Report) recovery reschedule
 */

export type ConversationStep =
  | "INIT"
  | "CONSENT_PROMPT"
  | "OPTED_OUT"
  | "ADDRESS_REVIEW"
  | "AWAITING_LANDMARK"
  | "SLOT_SELECTION"
  | "SAFE_FOR_DISPATCH"
  | "NDR_ALERT"
  | "NDR_RESCHEDULED";

export interface ChatMessage {
  id: string;
  sender: "bot" | "user";
  text: string;
  timestamp: string;
  quickReplies?: string[];
  status?: "sent" | "delivered" | "read";
}

export interface ConversationState {
  step: ConversationStep;
  messages: ChatMessage[];
  orderId: string;
  customerName: string;
  streetAddress: string;
  addressQuality: "Complete" | "NeedsLandmark" | "Poor";
  landmark: string | null;
  deliverySlot: string | null;
  isTyping: boolean;
}

export type ConversationAction =
  | { type: "START_CONVERSATION"; orderId: string; customerName: string; address: string; quality: "Complete" | "NeedsLandmark" | "Poor" }
  | { type: "SEND_USER_MESSAGE"; text: string }
  | { type: "RECEIVE_BOT_MESSAGE"; text: string; quickReplies?: string[]; nextStep?: ConversationStep }
  | { type: "SET_TYPING"; isTyping: boolean }
  | { type: "TRIGGER_NDR_SIMULATION" };

function getNowTimestamp(): string {
  const now = new Date();
  return now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function conversationReducer(
  state: ConversationState,
  action: ConversationAction,
): ConversationState {
  switch (action.type) {
    case "START_CONVERSATION": {
      const initialBotMessage: ChatMessage = {
        id: `msg_${Date.now()}`,
        sender: "bot",
        text: `Hi ${action.customerName}! 👋 Thank you for your order with ReturnZero. We're getting your shipment ready. Reply YES to confirm delivery updates, or STOP to opt out.`,
        timestamp: getNowTimestamp(),
        quickReplies: ["YES, Confirm Updates", "STOP"],
        status: "read",
      };

      return {
        ...state,
        orderId: action.orderId,
        customerName: action.customerName,
        streetAddress: action.address,
        addressQuality: action.quality,
        step: "CONSENT_PROMPT",
        messages: [initialBotMessage],
        isTyping: false,
      };
    }

    case "SET_TYPING":
      return { ...state, isTyping: action.isTyping };

    case "RECEIVE_BOT_MESSAGE": {
      const newBotMsg: ChatMessage = {
        id: `msg_${Date.now()}`,
        sender: "bot",
        text: action.text,
        timestamp: getNowTimestamp(),
        quickReplies: action.quickReplies,
        status: "read",
      };
      return {
        ...state,
        isTyping: false,
        step: action.nextStep ?? state.step,
        messages: [...state.messages, newBotMsg],
      };
    }

    case "SEND_USER_MESSAGE": {
      const userText = action.text.trim();
      const newUserMsg: ChatMessage = {
        id: `msg_${Date.now()}`,
        sender: "user",
        text: userText,
        timestamp: getNowTimestamp(),
        status: "read",
      };

      const updatedMessages = [...state.messages, newUserMsg];

      // Opt-out handling per ADR-015
      if (userText.toUpperCase() === "STOP") {
        return {
          ...state,
          step: "OPTED_OUT",
          messages: updatedMessages,
          isTyping: true,
        };
      }

      return {
        ...state,
        messages: updatedMessages,
        isTyping: true,
      };
    }

    case "TRIGGER_NDR_SIMULATION": {
      const ndrMsg: ChatMessage = {
        id: `msg_${Date.now()}`,
        sender: "bot",
        text: `⚠️ Delivery Alert: Courier attempted delivery for order #${state.orderId} today but customer premise was locked or customer unavailable. Would you like to reschedule?`,
        timestamp: getNowTimestamp(),
        quickReplies: ["Reschedule Tomorrow Morning", "Reschedule Tomorrow Afternoon"],
        status: "read",
      };
      return {
        ...state,
        step: "NDR_ALERT",
        messages: [...state.messages, ndrMsg],
      };
    }

    default:
      return state;
  }
}
