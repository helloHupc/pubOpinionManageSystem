<template>
  <div class="container ">
    <LoginForm v-if="showLoginForm" @switch-to-register="showLoginForm = false" />
    <RegisterForm v-if="!showLoginForm" @switch-to-login="showLoginForm = true" />
  </div>
</template>

<script lang="ts">
import { LoginForm, RegisterForm } from './components'
import {defineComponent, ref} from "vue";

export default defineComponent({
  components: {
    LoginForm,
    RegisterForm
  },
  setup() {

    const showLoginForm = ref(true);

    return {
      showLoginForm,
    }
  },
});
</script>

<style lang="scss" scoped>
.container{
    width: 100%;
    height: 100%;
    background: url("../assets/login_bg.jpg") no-repeat center center;
    background-size: cover;
    text-align: center;
    padding: 1px;
    overflow-y: auto;
}


</style>
