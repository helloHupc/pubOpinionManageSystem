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
      <h2>舆情管理系统-注册</h2>

      <el-form-item label="账号" prop="username">
        <el-input v-model="formData.username" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="密码" prop="password1">
        <el-input
            v-model="formData.password1"
            type="password"
            autocomplete="off"
            show-password
        />
      </el-form-item>
      <el-form-item label="确认密码" prop="password2">
        <el-input
            v-model="formData.password2"
            type="password"
            autocomplete="off"
            show-password
        />
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
      <el-input
          v-model="formData.email" 
          type="email"
      />
    </el-form-item>
      <el-form-i class="forget-password">
        <a href="javascript:void (0)" class="el-link el-link--primary" @click="resetForm()"><span class="el-link__inner">重置</span></a>
      </el-form-i>
      <el-form-item style="margin-top: 20px;">
        <el-button type="primary" class="common-btn" @click="submitForm(ruleFormRef)">注册</el-button>
      </el-form-item>
      <el-form-item>
        <el-button class="common-btn" @click="$emit('switch-to-login')">登录</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script lang="ts">
import {defineComponent, reactive, toRefs, ref, getCurrentInstance} from "vue";
import type { FormInstance, FormRules } from 'element-plus'
import {useRouter} from "vue-router";
import {register} from "@/request/api";

export default defineComponent( {
  name: 'RegisterForm',
    setup() {
    const formData = reactive({
        username: "",
        password1: "",
        password2: "",
        email:""
    })

    const rules = {
        username: [
          {required: true, message: '请输入账号', trigger: 'blur'},
          {min: 3, max: 10, message: '账号的长度在3-10之间', trigger: 'blur'},
        ],
        password1: [
          {required: true, message: '请输入密码', trigger: 'blur'},
          {min: 3, max: 10, message: '密码的长度在3-10之间', trigger: 'blur'},
        ],
        password2: [
          {required: true, message: '请输入密码', trigger: 'blur'},
          {min: 3, max: 10, message: '密码的长度在3-10之间', trigger: 'blur'},
        ],
        email: [
          {required: true,message: '请输入电子邮件地址',trigger: 'blur'},
          {type: 'email',message: '请输入正确的电子邮件地址',trigger: ['blur', 'change'],},
        ],
    }
    const ruleFormRef = ref<FormInstance>()
    const router = useRouter()
    const instance = getCurrentInstance()
    const submitForm = (formEl: FormInstance | undefined) => {
      if (!formEl) return
      formEl.validate((valid) => {
        if (valid) {
          register(formData).then((res)=>{
            console.log("register res",res)
            //跳转
            instance?.emit('switch-to-login')
          }).catch((e)=>{})
        } else {
          console.log('error submit!')
          return false
        }
      })
    }

    const resetForm = () => {
      formData.username = "";
      formData.password1 = "";
      formData.password2 = "";
      formData.email = "";
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
  .login-box {
    width: 100%;
    height: 100%;
    background: url("../../assets/login_bg.jpg") no-repeat center center;
    background-size: cover;
    text-align: center;
    padding: 1px;
  .demo-ruleForm{
    width: 500px;
    margin: 200px auto;
    background: #ffffff;
    padding: 40px;
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
}
</style>
