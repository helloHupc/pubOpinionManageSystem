<template>
  <div class="login-box">
    <el-form
        ref="ruleFormRef"
        :model="formData"
        status-icon
        :rules="rules"
        label-width="80px"
        :label-position="labelPosition"
        :size="size"
        class="demo-ruleForm"
    >
      <h2>舆情管理系统-登录</h2>

      <el-form-item label="账号" prop="username">
        <el-input v-model="formData.username" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input
            v-model="formData.password"
            type="password"
            autocomplete="off"
            show-password
        />
      </el-form-item>
      <el-form-i class="forget-password">
        <a href="javascript:void (0)" class="el-link el-link--primary" @click="resetForm()"><span class="el-link__inner">重置</span></a>
      </el-form-i>
      <el-form-item style="margin-top: 20px;">
        <el-button type="primary" class="common-btn" @click="submitForm(ruleFormRef)">登录</el-button>
      </el-form-item>
      <el-form-item>
        <el-button class="common-btn" @click="$emit('switch-to-register')">注册</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>


<script lang="ts">
import {defineComponent, reactive, toRefs, ref} from "vue";
import {LoginData} from "@/type/login";
import type { FormInstance, FormRules } from 'element-plus'
import {login} from "@/request/api";
import {useRouter} from "vue-router";
import { ElMessage } from 'element-plus';


export default defineComponent({
  name: 'LoginForm',
  setup() {
    const formData = reactive({
        username: "",
        password: ""
    })

    const rules = {
        username: [
          {required: true, message: '请输入账号', trigger: 'blur'},
          {min: 3, max: 10, message: '账号的长度在3-10之间', trigger: 'blur'},
        ],
        password: [
          {required: true, message: '请输入密码', trigger: 'blur'},
          {min: 3, max: 10, message: '密码的长度在3-10之间', trigger: 'blur'},
        ],
    }
    const ruleFormRef = ref<FormInstance>()
    const router = useRouter()
    const submitForm = (formEl: FormInstance | undefined) => {
      if (!formEl) return
      formEl.validate((valid) => {
        if (valid) {
          login(formData).then((res)=>{
            console.log("login res",res)
            ElMessage({
              message: res.message,
              grouping: false,
              type: 'success',
              duration: 2000
            })
            //保存token
            localStorage.setItem("token",res.token)
            //跳转
            router.push({ name: 'Home' })
          }).catch((e)=>{})
        } else {
          console.log('error submit!')
          return false
        }
      })
    }

    const resetForm = () => {
      formData.username = "";
      formData.password = "";
    }

    const labelPosition = "top"
    const size = "large"

    return {
      formData,
      rules,
      resetForm,
      ruleFormRef,
      submitForm,
      labelPosition,
      size
    }
  },
});
</script>

<style lang="scss" scoped>
  .demo-ruleForm{
    width: 500px;
    margin: 100px auto;
    background: #ffffff;
    padding: 30px;
    border-radius: 5px;
  }
  .common-btn{
    width: 100%;
  }
  .forget-password{
    margin-right: -85%;
  }
  h2{
    margin-bottom: 20px;
  }

</style>