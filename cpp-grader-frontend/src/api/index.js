import axios from 'axios'


const api = axios.create({
baseURL: '/api', // 根据后端实际路径调整
timeout: 60000,
})


export async function ocrUpload(formData) {
// POST /api/ocr 接受 form-data file
const res = await api.post('/ocr', formData, {
headers: { 'Content-Type': 'multipart/form-data' },
})
return res.data
}


export async function aiGrade(payload) {
// POST /api/ai_grade 接受 JSON { text: '...' }
const res = await api.post('/ai_grade', payload)
return res.data
}


export default api