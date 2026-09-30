<script setup lang="ts">

import { ref, onMounted } from "vue";
const health = ref('')

onMounted(async()=>{
    const res = await fetch ('http://127.0.0.1:8001/health')
    health.value = JSON.stringify(await res.json());
})
</script>

<template>
    <h1>Learn Assistant</h1>
    <p>后端状态:{{ health }}</p> 
</template>
