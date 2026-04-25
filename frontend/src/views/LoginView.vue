<template>
  <div class="min-h-screen flex relative overflow-hidden bg-[#030014]">
    <!-- Left: Branding (Desktop) -->
    <div class="hidden lg:flex lg:w-1/2 relative overflow-hidden items-center justify-center" style="background: linear-gradient(135deg, #1a0a2e 0%, #0f0c29 50%, #050210 100%)">
      <!-- Purple glow overlay -->
      <div class="absolute inset-0" style="background: radial-gradient(ellipse at center, rgba(147,51,234,0.15) 0%, transparent 70%)"></div>

      <!-- CSS-only particles -->
      <div class="particle" style="top: 12%; left: 8%; width: 140px; height: 140px; background: radial-gradient(circle, rgba(147,51,234,0.2) 0%, transparent 70%); animation: drift1 12s ease-in-out infinite 0s;"></div>
      <div class="particle" style="top: 50%; right: 8%; width: 100px; height: 100px; background: radial-gradient(circle, rgba(99,102,241,0.2) 0%, transparent 70%); animation: drift2 10s ease-in-out infinite 2s;"></div>
      <div class="particle" style="bottom: 12%; left: 18%; width: 60px; height: 60px; background: radial-gradient(circle, rgba(99,102,241,0.25) 0%, transparent 70%); animation: drift3 8s ease-in-out infinite 1s;"></div>
      <div class="particle" style="top: 8%; right: 22%; width: 40px; height: 40px; background: radial-gradient(circle, rgba(147,51,234,0.3) 0%, transparent 70%); animation: drift2 14s ease-in-out infinite 3s;"></div>
      <div class="particle" style="bottom: 22%; left: 42%; width: 80px; height: 80px; background: radial-gradient(circle, rgba(147,51,234,0.15) 0%, transparent 70%); animation: drift1 11s ease-in-out infinite 4s;"></div>
      <div class="particle" style="top: 38%; left: 4%; width: 50px; height: 50px; background: radial-gradient(circle, rgba(99,102,241,0.2) 0%, transparent 70%); animation: drift3 9s ease-in-out infinite 0.5s;"></div>

      <!-- Content -->
      <div class="relative z-10 text-center px-12 max-w-lg">
        <!-- Logo with pulse glow -->
        <div class="mb-8">
          <div class="logo-glow inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-white/10 backdrop-blur-sm border border-purple-400/30 mb-6">
            <svg class="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
            </svg>
          </div>
        </div>

        <h2 class="text-4xl font-bold text-white mb-4">OpenClawHub</h2>

        <p class="text-lg leading-relaxed">
          <span class="typewriter-text text-purple-200/80">AI 智能体协作平台</span><br/>
          <span class="fade-in-delayed text-purple-200/60">让团队与 AI 高效协同工作</span>
        </p>

        <div class="mt-10 flex justify-center gap-8 text-sm">
          <div class="feature-tag text-center" style="animation-delay: 2s">
            <div class="text-2xl font-bold text-white/90 mb-1">AI</div>
            <div class="text-purple-200/60">智能体管理</div>
          </div>
          <div class="feature-tag text-center" style="animation-delay: 2.2s">
            <div class="text-2xl font-bold text-white/90 mb-1">+</div>
            <div class="text-purple-200/60">任务编排</div>
          </div>
          <div class="feature-tag text-center" style="animation-delay: 2.4s">
            <div class="text-2xl font-bold text-white/90 mb-1">+</div>
            <div class="text-purple-200/60">团队协作</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right: Form -->
    <div class="w-full lg:w-1/2 flex items-center justify-center bg-[#050210] lg:bg-slate-950 px-6 py-12 relative overflow-hidden">
      <!-- Mobile particles -->
      <div class="particle lg:hidden" style="top: 8%; right: 10%; width: 100px; height: 100px; background: radial-gradient(circle, rgba(147,51,234,0.15) 0%, transparent 70%); animation: drift2 12s ease-in-out infinite 0s;"></div>
      <div class="particle lg:hidden" style="bottom: 18%; left: 5%; width: 70px; height: 70px; background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%); animation: drift1 10s ease-in-out infinite 1s;"></div>
      <div class="particle lg:hidden" style="top: 32%; left: 12%; width: 50px; height: 50px; background: radial-gradient(circle, rgba(147,51,234,0.2) 0%, transparent 70%); animation: drift3 8s ease-in-out infinite 2s;"></div>
      <div class="particle lg:hidden" style="bottom: 8%; right: 18%; width: 80px; height: 80px; background: radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%); animation: drift1 11s ease-in-out infinite 3s;"></div>

      <!-- Mobile purple glow -->
      <div class="absolute inset-0 lg:hidden" style="background: radial-gradient(ellipse at top, rgba(147,51,234,0.08) 0%, transparent 60%)"></div>

      <div class="w-full max-w-md relative z-10">
        <!-- Mobile logo (matching desktop style) -->
        <div class="lg:hidden text-center mb-8">
          <div class="logo-glow inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-white/10 backdrop-blur-sm border border-purple-400/30 mb-4">
            <svg class="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z" />
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-white">OpenClawHub</h1>
        </div>

        <!-- Glassmorphism card -->
        <div class="bg-black/40 backdrop-blur-xl border border-purple-500/20 rounded-2xl p-6 sm:p-8 shadow-xl shadow-purple-500/10">
          <h2 class="text-2xl font-bold text-white mb-2">欢迎回来</h2>
          <p class="text-slate-400 mb-8">登录你的账号以继续</p>

          <!-- Error message -->
          <Transition name="slide-fade">
            <div v-if="error" class="mb-6 px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-start gap-2">
              <svg class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
              </svg>
              <span>{{ error }}</span>
            </div>
          </Transition>

          <form @submit.prevent="handleLogin" class="space-y-5">
            <!-- Email with floating label -->
            <div class="relative">
              <input
                id="login-email"
                v-model="email"
                type="email"
                class="float-input w-full pl-11 pr-4 py-3.5 bg-white/5 border border-slate-700/50 rounded-xl text-white placeholder-transparent focus:outline-none focus:border-purple-500/50 focus:shadow-[0_0_20px_rgba(147,51,234,0.15)] transition-all duration-300"
                placeholder=" "
                required
              />
              <label for="login-email" class="float-label">邮箱</label>
              <div class="input-icon-wrap absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                <svg class="w-5 h-5 text-slate-500 transition-colors duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
                </svg>
              </div>
            </div>

            <!-- Password with floating label -->
            <div class="relative">
              <input
                id="login-password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                class="float-input w-full pl-11 pr-12 py-3.5 bg-white/5 border border-slate-700/50 rounded-xl text-white placeholder-transparent focus:outline-none focus:border-purple-500/50 focus:shadow-[0_0_20px_rgba(147,51,234,0.15)] transition-all duration-300"
                placeholder=" "
                required
              />
              <label for="login-password" class="float-label">密码</label>
              <div class="input-icon-wrap absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                <svg class="w-5 h-5 text-slate-500 transition-colors duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
                </svg>
              </div>
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-500 hover:text-purple-400 transition-colors duration-300"
              >
                <svg v-if="!showPassword" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
                </svg>
              </button>
            </div>

            <!-- Login button with gradient + shine -->
            <button
              type="submit"
              :disabled="loading"
              class="btn-login relative overflow-hidden w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-3.5 rounded-xl font-medium focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-black transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span class="relative z-10 flex items-center justify-center gap-2">
                <svg v-if="loading" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ loading ? '登录中...' : '登录' }}
              </span>
            </button>
          </form>
        </div>

        <p class="mt-8 text-center text-slate-500 text-sm">
          还没有账号？
          <router-link to="/register" class="text-purple-400 hover:text-purple-300 font-medium transition">注册新账号</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)
const router = useRouter()
const authStore = useAuthStore()

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    await authStore.login(email.value, password.value)
    router.push('/orgs')
  } catch (e: any) {
    const msg = e?.response?.data?.message || e?.message || '登录失败，请检查邮箱和密码'
    error.value = msg
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ===== Particle System (CSS only) ===== */
.particle {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  will-change: transform, opacity;
}

@keyframes drift1 {
  0%, 100% { transform: translateY(0) translateX(0) scale(1); opacity: 0.2; }
  33% { transform: translateY(-20px) translateX(15px) scale(1.08); opacity: 0.35; }
  66% { transform: translateY(-10px) translateX(-8px) scale(0.95); opacity: 0.25; }
}

@keyframes drift2 {
  0%, 100% { transform: translateY(0) translateX(0) scale(1); opacity: 0.15; }
  50% { transform: translateY(-30px) translateX(-12px) scale(1.12); opacity: 0.3; }
}

@keyframes drift3 {
  0%, 100% { transform: translateY(0) translateX(0) scale(1); opacity: 0.25; }
  40% { transform: translateY(-15px) translateX(8px) scale(1.05); opacity: 0.4; }
  80% { transform: translateY(-25px) translateX(-5px) scale(0.98); opacity: 0.2; }
}

/* ===== Logo Pulse Glow ===== */
.logo-glow {
  animation: pulse-glow 3s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 20px rgba(147, 51, 234, 0.3), inset 0 0 20px rgba(147, 51, 234, 0.05);
  }
  50% {
    box-shadow: 0 0 40px rgba(147, 51, 234, 0.6), 0 0 80px rgba(147, 51, 234, 0.3), inset 0 0 30px rgba(147, 51, 234, 0.1);
  }
}

/* ===== CSS-only Typewriter Effect ===== */
.typewriter-text {
  display: inline-block;
  clip-path: inset(0 100% 0 0);
  animation: typewriter-reveal 1.5s ease-out 0.3s forwards;
}

.typewriter-text::after {
  content: '';
  display: inline-block;
  width: 2px;
  height: 1.2em;
  background: rgba(167, 139, 250, 0.8);
  margin-left: 3px;
  vertical-align: text-bottom;
  animation: blink-cursor 0.75s step-end infinite, cursor-fade 0.5s ease 2.2s forwards;
}

@keyframes typewriter-reveal {
  to { clip-path: inset(0 0 0 0); }
}

@keyframes blink-cursor {
  from, to { opacity: 0; }
  50% { opacity: 1; }
}

@keyframes cursor-fade {
  to { opacity: 0; }
}

/* ===== Fade In Delayed ===== */
.fade-in-delayed {
  opacity: 0;
  animation: fade-in-up 0.8s ease 2s forwards;
}

@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ===== Feature Tags Stagger Animation ===== */
.feature-tag {
  opacity: 0;
  animation: fade-up 0.6s ease forwards;
}

@keyframes fade-up {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ===== Floating Label ===== */
.float-label {
  position: absolute;
  left: 2.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  pointer-events: none;
  padding: 0 0.375rem;
}

.float-input:focus ~ .float-label,
.float-input:not(:placeholder-shown) ~ .float-label {
  top: 0;
  transform: translateY(-50%) scale(0.85);
  color: #a855f7;
  background: linear-gradient(to bottom, transparent 45%, #050210 45%);
}

/* ===== Input Focus Icon Color ===== */
.float-input:focus ~ .input-icon-wrap svg {
  color: #a855f7;
}

/* ===== Button Shine Effect ===== */
.btn-login::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.btn-login:hover:not(:disabled)::before {
  left: 100%;
}

.btn-login:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(147, 51, 234, 0.3);
}

.btn-login:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
}

/* ===== Slide-Fade Transition (error message) ===== */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}
.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}
.slide-fade-enter-from {
  transform: translateY(-8px);
  opacity: 0;
}
.slide-fade-leave-to {
  transform: translateY(-4px);
  opacity: 0;
}
</style>
