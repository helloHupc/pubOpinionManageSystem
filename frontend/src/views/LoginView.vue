<template>
  <div class="login-container">
    <h1>登录</h1>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="username">用户名</label>
        <input type="text" id="username" v-model="username" required />
      </div>
      <div class="form-group">
        <label for="password">密码</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <button type="submit">登录</button>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import axiosInstance from '../axiosConfig';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
      router: useRouter(),
    };
  },

  methods: {
    async handleLogin() {
      try {

        const response = await axiosInstance.post('/login', {
          username: this.username,
          password: this.password,
        });
        console.log('Login successful:', response.data);
        const token = response.data.token;
        localStorage.setItem('token', token);

        console.log('Router object:', this.router);
        // 跳转到home页面
        this.router.push({ name: 'Home' });
      } catch (error) {
        console.error('Login failed:', error);
        // handle error (e.g., show error message)
      }
    },
  },
});
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
}

input {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #007BFF;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}
</style>
