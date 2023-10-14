import { defineStore } from 'pinia';
import { ref, nextTick } from 'vue';
import type { Ref } from 'vue';

type MessageLevelTag = 'error' | 'success' | string;

interface Message {
  message: string;
  levelTag: MessageLevelTag;
}

const useMessagesStore = defineStore('messages', () => {
  const messages: Ref<Array<Message>> = ref([]);

  const sendMessage = (message: string, levelTag: MessageLevelTag) => {
    // Remove message if it already exists
    messages.value = messages.value.filter(
      (msg) => !(msg.message === message && msg.levelTag === levelTag),
    );
    // Add (or re-add) message in next tick
    nextTick(() => {
      messages.value.push({ message, levelTag });
    });
  };

  return { sendMessage, messages };
});

export { useMessagesStore };
export type { MessageLevelTag, Message };
