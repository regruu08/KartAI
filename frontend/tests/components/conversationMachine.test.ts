import { describe, it, expect } from "vitest";
import {
  conversationReducer,
  type ConversationState,
} from "../../components/simulator/conversationMachine";

describe("WhatsApp Simulator Conversation Machine", () => {
  const initialBaseState: ConversationState = {
    step: "INIT",
    messages: [],
    orderId: "ORD-TEST-123",
    customerName: "Aarav Patel",
    streetAddress: "Flat 201, Shanti Niketan",
    addressQuality: "NeedsLandmark",
    landmark: null,
    deliverySlot: null,
    isTyping: false,
  };

  it("handles START_CONVERSATION and prompts for consent", () => {
    const state = conversationReducer(initialBaseState, {
      type: "START_CONVERSATION",
      orderId: "ORD-TEST-123",
      customerName: "Aarav Patel",
      address: "Flat 201, Shanti Niketan",
      quality: "NeedsLandmark",
    });

    expect(state.step).toBe("CONSENT_PROMPT");
    expect(state.messages).toHaveLength(1);
    expect(state.messages[0]?.text).toContain("Hi Aarav Patel!");
    expect(state.messages[0]?.quickReplies).toContain("STOP");
  });

  it("handles STOP opt-out immediately per ADR-015", () => {
    const started = conversationReducer(initialBaseState, {
      type: "START_CONVERSATION",
      orderId: "ORD-TEST-123",
      customerName: "Aarav Patel",
      address: "Flat 201, Shanti Niketan",
      quality: "NeedsLandmark",
    });

    const optedOut = conversationReducer(started, {
      type: "SEND_USER_MESSAGE",
      text: "STOP",
    });

    expect(optedOut.step).toBe("OPTED_OUT");
    expect(optedOut.messages).toHaveLength(2);
    expect(optedOut.messages[1]?.text).toBe("STOP");
  });

  it("advances through landmark clarification to slot selection", () => {
    const started = conversationReducer(initialBaseState, {
      type: "START_CONVERSATION",
      orderId: "ORD-TEST-123",
      customerName: "Aarav Patel",
      address: "Flat 201, Shanti Niketan",
      quality: "NeedsLandmark",
    });

    // User agrees to updates
    const agreed = conversationReducer(started, {
      type: "SEND_USER_MESSAGE",
      text: "YES, Confirm Updates",
    });

    // Bot asks for landmark
    const askLandmark = conversationReducer(agreed, {
      type: "RECEIVE_BOT_MESSAGE",
      text: "Please provide a landmark",
      nextStep: "AWAITING_LANDMARK",
    });
    expect(askLandmark.step).toBe("AWAITING_LANDMARK");

    // User provides landmark
    const provided = conversationReducer(askLandmark, {
      type: "SEND_USER_MESSAGE",
      text: "Near Metro Pillar 45",
    });

    // Bot asks for delivery slot
    const askSlot = conversationReducer(provided, {
      type: "RECEIVE_BOT_MESSAGE",
      text: "Choose delivery slot",
      nextStep: "SLOT_SELECTION",
    });
    expect(askSlot.step).toBe("SLOT_SELECTION");
  });

  it("handles NDR simulation trigger", () => {
    const state = conversationReducer(initialBaseState, {
      type: "TRIGGER_NDR_SIMULATION",
    });

    expect(state.step).toBe("NDR_ALERT");
    expect(state.messages[0]?.text).toContain("Delivery Alert");
  });
});
