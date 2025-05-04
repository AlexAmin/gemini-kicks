<template>
  <div class="bg-gray-800 rounded-lg p-6">
    <h2 class="text-xl font-semibold mb-4">{{title}}</h2>
    <div class="space-y-4">
      <LoadingComponent v-if="clips.length === 0"/>
      <ListItemTransition v-else>
      <div  v-for="clip in clips" :key="clip"
           class="bg-gray-700 rounded-lg p-4 hover:bg-gray-600 transition-colors duration-200">
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-3">
            <div class="bg-gray-800 p-2 rounded-lg">
              <PhVideo class="text-blue-400" :size="24"/>
            </div>
            <div>
              <div class="font-medium">{{clip}}</div>
              <div class="text-sm text-gray-400">{{ formatDuration(clip) }}</div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <div
                class="px-3 py-1 rounded-full text-sm"
                :class="{
                'bg-green-400/20 text-green-400': true
              }"
            >
              Completed
            </div>
            <PhDownload
                class="text-gray-400 hover:text-white cursor-pointer"
                :size="20"
            />
          </div>
        </div>
        <div class="text-sm text-gray-400 mt-2">
          {{ formatPlayers(clip) }}
        </div>
      </div>
      </ListItemTransition>
    </div>
  </div>
</template>

<script setup lang="ts">
import {PhDownload, PhVideo} from "@phosphor-icons/vue";
import LoadingComponent from "./LoadingComponent.vue";
import ListItemTransition from "./transition/ListItemTransition.vue";
import {formatSeconds} from "../util/formatSeconds.ts";

defineProps<{
  title: string
  clips: string[];
}>();

function formatDuration(fileName: string): string {
  const split: string[] = fileName.split("-")
      .map((item)=>item.split(".mp3")[0].split(".mp4")[0].split(".wav")[0])
  return `${formatSeconds(split[2])} - ${formatSeconds(split[3])}`
}

function formatPlayers(fileName: string): string {
  const split: string[] = fileName.split("-")
  if(split[1]==="?") return "No players recognized"
  else return split[1]
}

function formatTimestamp(timestamp: string): string {
  return new Date(timestamp).toLocaleString();
}
</script>