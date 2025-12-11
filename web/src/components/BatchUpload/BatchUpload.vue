<template>
  <div class="batch-page-container">
    <div class="batch-container">
      
      <div class="batch-header">
        <div class="header-title">📚 批量作业上传工作台</div>
        <div class="header-actions">
          <a-button type="primary" @click="addBatch">
            <template #icon><icon-plus /></template> 新增作业批次
          </a-button>
          <a-button type="primary" status="success" @click="confirmUpload" :loading="loading">
            <template #icon><icon-check /></template> 确认上传全部
          </a-button>
        </div>
        <div class="close-overlay-btn" @click="handleClose" title="返回">
          <icon-close />
        </div>
      </div>

      <div class="batch-list-container" ref="scrollContainer">
        <div v-for="(batch, bIndex) in batches" :key="batch.id" class="batch-card">
          <div class="card-header">
            <div><span class="batch-title">{{ batch.title }}</span><span class="batch-info">共 {{ batch.files.length }} 张图片</span></div>
            <div class="card-actions">
              <a-button type="text" status="danger" size="small" @click="removeBatch(bIndex)">删除批次</a-button>
              <input type="file" multiple accept="image/*" style="display:none" :ref="(el) => setInputRef(el, batch.id)" @change="(e) => handleAddFiles(bIndex, e)" />
              <a-button type="outline" size="small" @click="triggerFileInput(batch.id)">+ 继续添加</a-button>
            </div>
          </div>
          <div class="image-grid">
            <div v-for="(file, fIndex) in batch.files" :key="fIndex" class="img-item">
              <img :src="file.url">
              <div class="img-mask"><span class="mask-btn" @click="handlePreview(file)">预览</span><span class="mask-btn del" @click="removeFile(bIndex, fIndex)">删除</span></div>
            </div>
            <div class="add-img-placeholder" @click="triggerFileInput(batch.id)"><icon-plus style="font-size: 20px;" /><span style="font-size:12px">上传图片</span></div>
          </div>
        </div>
        <a-empty v-if="batches.length === 0" description="点击上方“新增作业批次”开始" />
      </div>
    </div>

    <a-modal v-model:visible="previewVisible" :footer="false" width="auto">
      <img :src="previewImage" style="max-width: 80vw; max-height: 80vh;">
    </a-modal>
  </div>
</template>
<script src="./BatchUpload.js"></script>

<style scoped src="./BatchUpload.css"></style>