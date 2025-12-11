// 1. Imports
import { ref, reactive, nextTick, onMounted } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import { IconCheck, IconPlus, IconClose } from '@arco-design/web-vue/es/icon'
import { useRouter } from 'vue-router' 
import { uploadAssignmentBatchAPI } from '../../api/assignment.js'
export default {
   components: {
     IconCheck, IconPlus, IconClose
    
  },
setup(){
const router = useRouter() 

const loading = ref(false)
const batches = ref([])
const fileInputRefs = ref({})
const scrollContainer = ref(null)
const previewVisible = ref(false)
const previewImage = ref('')
const fileFingerprints = new Set()

const setInputRef = (el, id) => { if (el) fileInputRefs.value[id] = el }
const generateId = () => '_' + Math.random().toString(36).substr(2, 9)

const addBatch = () => {
  batches.value.push({ id: generateId(), title: `作业批次 #${batches.value.length + 1}`, files: [] })
  nextTick(() => { if(scrollContainer.value) scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight })
}

const removeBatch = (index) => { 
  const batch = batches.value[index]
  // 移除该批次下所有文件的指纹
  batch.files.forEach(f => fileFingerprints.delete(`${f.name}_${f.size}`))
  
  delete fileInputRefs.value[batch.id]; 
  batches.value.splice(index, 1) 
}

const triggerFileInput = (batchId) => { const el = fileInputRefs.value[batchId]; if (el) el.click() }

const handleAddFiles = (batchIndex, event) => {
  const files = Array.from(event.target.files)
  const targetBatch = batches.value[batchIndex]
  let duplicateCount = 0

  files.forEach(file => {
    // 简单指纹：文件名 + 大小
    const fingerprint = `${file.name}_${file.size}`
    
    if (fileFingerprints.has(fingerprint)) {
      duplicateCount++
    } else {
      fileFingerprints.add(fingerprint)
      file.url = URL.createObjectURL(file) 
      targetBatch.files.push(file)
    }
  })

  event.target.value = '' // 清空 input
  
  if (duplicateCount > 0) {
    Message.warning(`已自动过滤 ${duplicateCount} 张重复图片`)
  }
}

const removeFile = (bIdx, fIdx) => {
  const file = batches.value[bIdx].files[fIdx]
  // 移除指纹
  fileFingerprints.delete(`${file.name}_${file.size}`)
  batches.value[bIdx].files.splice(fIdx, 1)
}


const handlePreview = (f) => { previewImage.value = f.url; previewVisible.value = true }

const confirmUpload = async () => {
  if (batches.value.every(b => b.files.length === 0)) return Message.warning('请添加图片')
  loading.value = true
  try {
    const promises = batches.value.filter(b=>b.files.length>0).map(async b => {
      const fd = new FormData(); fd.append('title', b.title); b.files.forEach(f => fd.append('files', f))
      try { return await uploadAssignmentBatchAPI(fd) } catch(e) { return null }
    })
    const res = await Promise.all(promises)
    const success = res.filter(r => r && r.code === 0).map((r, i) => ({ ...r.data, localFiles: batches.value[i].files }))
    
    if (success.length > 0) {
      Message.success(`成功上传 ${success.length} 个批次`)
      sessionStorage.setItem('temp_batch_uploads', JSON.stringify(success))
      handleClose()
    } else {
      Message.warning('所有批次上传失败')
    }
  } catch(e) { Message.error('上传异常') } 
  finally { loading.value = false }
}

const handleClose = () => {
  router.push('/grader')
}

onMounted(() => { if(batches.value.length === 0) addBatch() })
return{
router,loading,batches,scrollContainer,previewVisible,fileInputRefs,fileFingerprints,generateId,addBatch,
setInputRef,removeBatch,triggerFileInput,handleAddFiles,removeFile, handlePreview,
confirmUpload,previewImage,
loading,
batches,
fileInputRefs,
scrollContainer,
previewVisible,
previewImage,
fileFingerprints,
setInputRef,
generateId,
addBatch,
removeBatch,
triggerFileInput,
handleAddFiles,
removeFile,
handlePreview,
confirmUpload,
handleClose,
}
}
}