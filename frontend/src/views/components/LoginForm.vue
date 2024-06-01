<template>
  <div class="login-box">
    <el-form
        ref="ruleFormRef"
        :model="ruleForm"
        status-icon
        :rules="rules"
        label-width="80px"
        :label-position="labelPosition"
        :size="size"
        class="demo-ruleForm"
    >
      <h2>舆情管理系统-登录</h2>

      <el-form-item label="账号" prop="username">
        <el-input v-model="ruleForm.username" autocomplete="off"/>
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input
            v-model="ruleForm.password"
            type="password"
            autocomplete="off"
            show-password
        />
      </el-form-item>
      <el-form-i class="forget-password">
        <a href="javascript:void (0)" class="el-link el-link--primary" @click="resetForm(ruleFormRef)"><span class="el-link__inner">重置</span></a>
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


export default defineComponent({
  name: 'LoginForm',
  setup() {
    const data = reactive(new LoginData())

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
          login(data.ruleForm).then((res)=>{
            console.log("res",res)
            //保存token
            localStorage.setItem("token",res.data.token)
            //跳转
            router.push({ name: 'Home' })
          })
        } else {
          console.log('error submit!')
          return false
        }
      })
    }

    const resetForm = () => {
      data.ruleForm.username = "";
      data.ruleForm.password = "";
    }

    const labelPosition = "top"
    const size = "large"

    return {
      ...toRefs(data),
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