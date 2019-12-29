<template>
  <div id="app">
    <camera-obscura msg="Welcome to Your Vue.js App"/>
  </div>
</template>

<script>
import CameraObscura from './components/CameraObscura.vue'

export default {
  name: 'app',
  components: {
    CameraObscura
  }
}
</script>

<style>
body {
  background-color: black;
}
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #ffffff;
  margin-top: 60px;
  
}
</style>
