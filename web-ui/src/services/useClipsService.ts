import {ref} from "vue";
import axios from "axios";
import {GenerationFiles} from "../types/generation.ts";
import {StatusResponse} from "../types/statusResponse.ts";

export function useClipsService() {
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const fetchClips = async (): Promise<GenerationFiles> => {
    try {
      isLoading.value = true;
      error.value = null;
      const response = await axios.get('http://localhost:8080/files');
      return response.data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch clips';
      return {files:{}}
    } finally {
      isLoading.value = false;
    }
  };


  const fetchGenerationStatus = async (): Promise<StatusResponse> => {
    try {
      isLoading.value = true;
      error.value = null;
      const response = await axios.get('http://localhost:8080/status');
      return response.data.status
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch status';
      throw error.value;
    } finally {
      isLoading.value = false;
    }
  };

  return {
    isLoading,
    error,
    fetchClips,
    fetchGenerationStatus
  };
}