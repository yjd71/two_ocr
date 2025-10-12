<template>
<el-container style="height:100vh; padding:20px;">
<el-header style="font-size:24px; font-weight:600;">C++作业批改系统</el-header>
<el-main>
<upload-grade />
</el-main>
</el-container>
</template>


<script setup>
import UploadGrade from './components/UploadGrade.vue'
</script>