<template>
  <transition-group
      class="flex flex-col gap-y-1"
      enter-active-class="transition-all duration-500 ease-in-out"
      enter-from-class="opacity-0 translate-x-8"
      enter-to-class="opacity-100 translate-x-0"
      move-class="transition-all duration-500 ease-in-out"
      tag="div"
  >
    <slot name="default"/>
  </transition-group>
</template>
<script lang="ts" setup>

</script>