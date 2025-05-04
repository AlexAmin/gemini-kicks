<template>
  <div class="min-h-screen bg-gray-900 text-white py-8">
    <div class="max-w-4xl mx-auto space-y-6 px-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <StatusComponent :status="status" :files="clips"/>
        <div class="bg-gray-800 rounded-lg p-6">
          <h2 class="text-xl font-semibold mb-4">Generation Status</h2>
          <div class="flex items-center gap-2">
            <div class="flex-1 flex flex-col">
              <div class="flex flex-row items-center gap-x-1">
                <PhBasketball/>
                <span class="font-bold">Teams</span>
                <span class="ml-auto">{{status.teams.length === 0 ? 'Analyzing' : status.teams}}</span>
              </div>
              <div class="flex flex-row gap-x-1 items-center">
                <PhFile/>
                <span class="font-bold">Status</span>
                <span
                    class="ml-auto"
                    :class="{
                    'text-yellow-400': status.status === 'processing',
                    'text-green-400': status.status === 'completed',
                    'text-red-400': status.status === 'failed',
                    'text-gray-400': status.status === 'not_started'
                  }"
                >
                  {{ parseStatus(status.status) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <ClipListComponent v-if="clips"
                         :clips="clips.files['highlights-audio']||[]"
                         title="Audio Highlights"/>
      <ClipListComponent v-if="clips"
                         :clips="clips.files['highlights-video']||[]"
                         title="Video Highlights"/>
      <ClipListComponent v-if="clips"
                         :clips="clips.files['full-summary']||[]"
                         title="Audio Summary"/>
    </div>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref} from "vue";
import {PhBasketball, PhFile, PhSpeakerHigh} from "@phosphor-icons/vue";
import StatusComponent from "./components/StatusComponent.vue";
import ClipListComponent from "./components/ClipListComponent.vue";
import {useClipsService} from "./services/useClipsService";
import {StatusResponse} from "./types/statusResponse.ts";
import {GenerationFiles} from "./types/generation.ts";

const clipsService = useClipsService();
const clips = ref<GenerationFiles | undefined>(undefined);
const status = ref<StatusResponse>({status: "", teams: "", full_duration: 0});

async function fetchData() {
  try {
    const [clipsData, statusResponse] = await Promise.all([
      clipsService.fetchClips(),
      clipsService.fetchGenerationStatus()
    ]);
    clips.value = clipsData
    status.value = statusResponse
  } catch (error) {
    console.error("Failed to fetch data:", error);
  }
}


function parseStatus(status: string): string {
  switch (status) {
    case "intro":
      return "Generating Audio Intro"
    case "generating":
      return "Analyzing and Generating Highlights"
  }
}

onMounted(() => {
  fetchData()
  // Poll for updates every 5 seconds
  setInterval(fetchData, 5000);
});
</script>