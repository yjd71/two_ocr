import { ref, reactive, onMounted,onActivated } from 'vue'
import { Message } from '@arco-design/web-vue'
import { 
  IconSearch, 
  IconRefresh, 
  IconSortAscending, 
  IconSortDescending, 
  IconDown, 
  IconDelete,
  IconCode, 
  IconComputer, 
  IconRobot, 
  IconThumbUpFill, 
  IconThumbDownFill, 
  IconBulb
} from '@arco-design/web-vue/es/icon'
import { 
  getAssignmentListAPI, 
  getAssignmentDetailAPI, 
  deleteAssignmentsAPI 
} from '../api/assignment.js'

export default {
  // 注册图标组件，供模板使用
  components: {
    IconSearch,
    IconRefresh,
    IconSortAscending,
    IconSortDescending,
    IconDown,
    IconDelete,
    IconCode, IconComputer, IconRobot, IconThumbUpFill, IconThumbDownFill, IconBulb
  },
  setup() {
    // --- 状态定义 ---
    const loading = ref(false)
    const detailLoading = ref(false)
    const tableData = ref([])
    
    // 多选相关
    const selectedKeys = ref([])
    const rowSelection = reactive({
      type: 'checkbox',
      showCheckedAll: true,
      onlyCurrent: false,
    })

    // 搜索表单
    const searchForm = reactive({
      fileName: '',
      status: ''
    })

    // 查询参数
    const queryParams = reactive({
      sortBy: 'createdAt',
      sortOrder: 'desc'
    })

    // 分页参数
    const pagination = reactive({
      current: 1,
      pageSize: 10,
      total: 0,
      showTotal: true,
      showJumper: true,
      showPageSize: true
    })

    // 详情弹窗数据
    const modals = reactive({ code: false, run: false, ai: false })
    const currentDetail = reactive({
      code: '',
      compileInfo: null,
      aiResult: null
    })

    // --- 核心业务逻辑 ---

    // 1. 获取列表数据
    const fetchData = async () => {
      loading.value = true
      try {
        // 构造 likes 数组 
        const likes = []
        if (searchForm.fileName) {
          likes.push(`fileName:${searchForm.fileName}`)
        }
        if (searchForm.status) {
          likes.push(`status:${searchForm.status}`)
        }

        const res = await getAssignmentListAPI({
          page: pagination.current,
          pageSize: pagination.pageSize,
          likes: likes, // 传递数组
          sortBy: queryParams.sortBy,
          sortOrder: queryParams.sortOrder
        })
// ------------------------------------------------------------

        //  MOCK 模拟数据 (模拟 50 条数据，支持分页效果)
        // await new Promise(r => setTimeout(r, 600)) // 模拟 600ms 网络延迟
        
        // 生成 10 条假数据，模拟不同状态
        // const mockList = Array.from({ length: 10 }, (_, i) => {
        //   const idBase = (pagination.current - 1) * 10 + i + 1000
          // 模拟状态分布
        //   let status = '已评分'
        //   let score = 80 + (i * 2) % 20
        //   if (i % 4 === 1) { status = '编译失败'; score = null }
        //   if (i % 4 === 2) { status = '识别成功'; score = null }
        //   if (i % 4 === 3) { status = '识别失败'; score = null }

        //   return {
        //     assignmentId: idBase,
        //     fileName: `C_Plus_Plus_Homework_${idBase}.cpp`,
        //     status: status,
        //     score: score,
        //     createdAt: '2025-11-29 14:30:00',
        //     updatedAt: '2025-11-29 14:35:00'
        //   }
        // })

        // const res = { 
        //   code: 0, 
        //   data: { 
        //     assignments: mockList, 
        //     pagination: { 
        //       page: pagination.current,
        //       pageSize: pagination.pageSize,
        //       total: 52, // 假装总共有 52 条
        //       totalPages: 6
        //     } 
        //   } 
        // }
        // ------------------------------------------------------------
        if (res.code === 0) {
          tableData.value = res.data.assignments
          pagination.total = res.data.pagination.total
          // 翻页或查询后清空选中，防止误操作
          selectedKeys.value = []
        } else {
          Message.error(res.message || '获取列表失败')
        }
      } catch (err) {
        Message.error('获取任务列表异常')
        console.error(err)
      } finally {
        loading.value = false
      }
    }

    // 2. 搜索与重置
    const handleSearch = () => {
      pagination.current = 1 // 重置到第一页
      fetchData()
    }

    const handleReset = () => {
      searchForm.fileName = ''
      searchForm.status = ''
      queryParams.sortBy = 'createdAt'
      queryParams.sortOrder = 'desc'
      handleSearch()
    }

    // 3. 排序切换
    const toggleSortOrder = () => {
      queryParams.sortOrder = queryParams.sortOrder === 'asc' ? 'desc' : 'asc'
      fetchData()
    }

    // 4. 分页事件
    const onPageChange = (page) => {
      pagination.current = page
      fetchData()
    }
    
    const onPageSizeChange = (pageSize) => {
      pagination.pageSize = pageSize
      pagination.current = 1
      fetchData()
    }

    // 5. 获取详情并打开预览
    const handlePreview = async (type, record) => {
      // 先打开弹窗并显示 Loading
      if (type === 'code') modals.code = true
      if (type === 'run') modals.run = true
      if (type === 'ai') modals.ai = true
      
      detailLoading.value = true
      
      try {
        const res = await getAssignmentDetailAPI(record.assignmentId)
        // ------------------------------------------------------------

        //  MOCK 模拟详情数据 (严格符合 api_assignments.md)
        // await new Promise(r => setTimeout(r, 800))
        
        // const res = {
        //   code: 0,
        //   data: {
        //     assignmentId: record.assignmentId,
        //     // OCR 结果
        //     ocrResult: { 
        //       recognizedCode: `#include <iostream>\nusing namespace std;\n\nint main() {\n    // 这是作业ID ${record.assignmentId} 的代码\n    cout << "Hello Testing!" << endl;\n    return 0;\n}` 
        //     },
        //     // 编译结果
        //     compileResult: {
        //       language: 'C++',
        //       codeLengthBytes: 256,
        //       submitTime: '2025-11-29 14:30:00',
        //       evalTime: '0.05s',
        //       compileSuccess: record.status !== '编译失败',
        //       output: record.status !== '编译失败' ? 'Hello Testing!\nProcess finished.' : null,
        //       error: record.status === '编译失败' ? 'Error: expected ";" before "return"' : null
        //     },
        //     // AI 评分报告 (仅当状态为已评分时返回)
        //     report: record.status === '已评分' ? {
        //       score: record.score,
        //       reason: '代码结构完整，逻辑清晰，但变量命名可以更规范。', // 对应 comment
        //       breakdown: {
        //         correctness: 90,
        //         standardization: 85,
        //         efficiency: 80,
        //         readability: 95
        //       },
        //       suggestions: [
        //         '建议使用更具描述性的变量名',
        //         '增加适当的注释说明算法逻辑'
        //       ],
        //       strengths: [ // 验证字段：优点
        //         '主函数结构标准',
        //         'IO流使用正确'
        //       ],
        //       weaknesses: [ // 验证字段：缺点
        //         '缺少头部注释',
        //         '魔术数字未定义常量'
        //       ],
        //       generatedAt: '2025-11-29 14:35:00'
        //     } : null
        //   }
        // }
        // ------------------------------------------------------------
        if (res.code === 0) {
          const data = res.data
          // 映射数据
          currentDetail.code = data.ocrResult?.recognizedCode || '未识别到代码'
          currentDetail.compileInfo = data.compileResult || null
          
          if (data.report) {
            currentDetail.aiResult = {
              score: data.report.score,
              comment: data.report.reason, // 映射 reason -> comment
              breakdown: data.report.breakdown,
              suggestions: data.report.suggestions,
              strengths: data.report.strengths,
              weaknesses: data.report.weaknesses
            }
          } else {
            currentDetail.aiResult = null
          }
        } else {
          Message.error(res.message || '获取详情失败')
        }
      } catch (err) {
        Message.error('获取详情请求异常')
      } finally {
        detailLoading.value = false
      }
    }

    // 6. 删除逻辑 (单删 & 批删)
    const handleDelete = async (ids) => {
      try {
        const res = await deleteAssignmentsAPI(ids)
        // ------------------------------------------------------------

        //  MOCK 模拟删除成功
        // await new Promise(r => setTimeout(r, 500))
        // const res = { code: 0 }
        // ------------------------------------------------------------
        if (res.code === 0) {
          Message.success(`成功删除 ${ids.length} 项任务`)
          // 如果当前页删光了且不是第一页，自动往前跳
          if (tableData.value.length === ids.length && pagination.current > 1) {
            pagination.current--
          }
          fetchData()
        } else {
          Message.error(res.message || '删除失败')
        }
      } catch (err) {
        Message.error('删除请求异常')
      }
    }

    const handleBatchDelete = () => {
      if (selectedKeys.value.length === 0) return
      handleDelete(selectedKeys.value)
    }

    // --- 工具函数 ---
    const getStatusColor = (status) => {
      if (!status) return 'gray'
      if (status.includes('成功') || status === '已评分') return 'green'
      if (status.includes('失败')) return 'red'
      return 'arcoblue'
    }

    const getScoreClass = (score) => {
      if (score >= 90) return 'score-high'
      if (score >= 60) return 'score-mid'
      return 'score-low'
    }

    // 初始化
    onMounted(() => {
      fetchData()
    })
    onActivated(() => {
      fetchData()
    })
    // 导出所有给模板
    return {
      loading,
      detailLoading,
      tableData,
      selectedKeys,
      rowSelection,
      searchForm,
      queryParams,
      pagination,
      modals,
      currentDetail,
      fetchData,
      handleSearch,
      handleReset,
      toggleSortOrder,
      onPageChange,
      onPageSizeChange,
      handlePreview,
      handleDelete,
      handleBatchDelete,
      getStatusColor,
      getScoreClass
    }
  }
}