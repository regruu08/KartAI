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
    expect(provided.landmark).toBe("Near Metro Pillar 45");

    // Bot asks for delivery slot
    const askSlot = conversationReducer(provided, {
      type: "RECEIVE_BOT_MESSAGE",
      text: "Choose delivery slot",
      nextStep: "SLOT_SELECTION",
    });
    expect(askSlot.step).toBe("SLOT_SELECTION");
    expect(askSlot.landmark).toBe("Near Metro Pillar 45");

    // User chooses slot
    const slotChosen = conversationReducer(askSlot, {
      type: "SEND_USER_MESSAGE",
      text: "Morning (9 AM - 1 PM)",
    });
    expect(slotChosen.deliverySlot).toBe("Morning (9 AM - 1 PM)");
    expect(slotChosen.landmark).toBe("Near Metro Pillar 45");
  });

  describe("Transition Table Tests", () => {
    it.each([
      { input: "Opposite City Hospital", expectedLandmark: "Opposite City Hospital", desc: "quick reply landmark" },
      { input: "Near Gate 2, Behind Police Chowki", expectedLandmark: "Near Gate 2, Behind Police Chowki", desc: "free text landmark" },
      { input: "   ", expectedLandmark: null, desc: "empty text leaves landmark null" },
    ])("AWAITING_LANDMARK with $desc sets landmark appropriately", ({ input, expectedLandmark }) => {
      const stateInLandmarkStep: ConversationState = {
        ...initialBaseState,
        step: "AWAITING_LANDMARK",
      };
      const result = conversationReducer(stateInLandmarkStep, {
        type: "SEND_USER_MESSAGE",
        text: input,
      });
      expect(result.landmark).toBe(expectedLandmark);
    });

    it("does not overwrite landmark on subsequent steps with slot text", () => {
      const stateWithLandmark: ConversationState = {
        ...initialBaseState,
        step: "SLOT_SELECTION",
        landmark: "Near Metro Pillar 120",
      };
      const result = conversationReducer(stateWithLandmark, {
        type: "SEND_USER_MESSAGE",
        text: "Afternoon (2 PM - 6 PM)",
      });
      expect(result.landmark).toBe("Near Metro Pillar 120");
      expect(result.deliverySlot).toBe("Afternoon (2 PM - 6 PM)");
    });
  });

  it("handles NDR simulation trigger", () => {
    const state = conversationReducer(initialBaseState, {
      type: "TRIGGER_NDR_SIMULATION",
    });

    expect(state.step).toBe("NDR_ALERT");
    expect(state.messages[0]?.text).toContain("Delivery Alert");
  });
});
