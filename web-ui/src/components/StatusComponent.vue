<template>
  <div class="bg-gray-800 rounded-lg p-6">
    <div class="flex flex-row mb-4 items-center gap-x-3">
      <h2 class="text-xl font-semibold">Generation Progress</h2>
      <LoadingComponent
          v-if="status.status !=='done'"
          h="h-5" w="h-5" class=""/>
    </div>
    <div class="space-y-4">
      <div>
        <div class="flex flex-row mb-2">
          <span>Time</span>
          <span class="ml-auto text-blue-400">{{
              formatSeconds(status.window_start)
            }} / {{ formatSeconds(status.full_duration) }}</span>
        </div>
        <div class="w-full bg-gray-700 rounded-full h-2">
          <div
              class="bg-blue-500 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${((status.status === 'done' ? status.full_duration : (status.window_start||0)) / status.full_duration) * 100}%` }"
          ></div>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-4 mt-4">
        <div v-if="files && files.files" class="bg-gray-700 rounded-lg p-4">
          <div class="text-sm text-gray-400">Total Clips</div>
          <div class="text-2xl font-semibold">{{ (files.files["highlights-video"]||[]).length + (files.files["highlights-audio"]||[]).length }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">

import {StatusResponse} from "../types/statusResponse.ts";
import LoadingComponent from "./LoadingComponent.vue";
import {formatSeconds} from "../util/formatSeconds.ts";
import {GenerationFiles} from "../types/generation.ts";

defineProps<{
  files?: GenerationFiles
  status: StatusResponse;
}>();


</script>