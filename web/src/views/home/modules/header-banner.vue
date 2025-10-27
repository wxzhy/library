<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { $t } from '@/locales';
import { useAppStore } from '@/store/modules/app';
import { useAuthStore } from '@/store/modules/auth';
import { fetchUserSummary } from '@/service/api';

defineOptions({ name: 'HeaderBanner' });

const appStore = useAppStore();
const authStore = useAuthStore();

const gap = computed(() => (appStore.isMobile ? 0 : 16));

interface StatisticData {
  id: number;
  title: string;
  value: number;
  formatter?: (val: number) => string;
}

const userBorrowStats = ref<Api.SystemManage.UserSummary>({
  total_borrows: 0,
  active_borrows: 0,
  overdue_borrows: 0
});

const statisticData = computed<StatisticData[]>(() => [
  {
    id: 0,
    title: '当前借阅',
    value: userBorrowStats.value.active_borrows,
    formatter: (val: number) => `${val}本`
  },
  {
    id: 1,
    title: '逾期图书',
    value: userBorrowStats.value.overdue_borrows,
    formatter: (val: number) => `${val}本`
  },
  {
    id: 2,
    title: '历史借阅',
    value: userBorrowStats.value.total_borrows,
    formatter: (val: number) => `${val}本`
  }
]);

// 获取用户借阅统计信息
async function getUserBorrowStats() {
  try {
    const { data } = await fetchUserSummary();
    if (data) {
      userBorrowStats.value = data;
    }
  } catch (error) {
    console.error('获取用户借阅统计失败:', error);
  }
}

onMounted(() => {
  getUserBorrowStats();
});
</script>

<template>
  <ElCard class="card-wrapper">
    <ElRow :gutter="gap" class="px-8px">
      <ElCol :md="18" :sm="24">
        <div class="flex-y-center">
          <div class="size-72px shrink-0 overflow-hidden rd-1/2">
            <img src="@/assets/imgs/soybean.jpg" class="size-full" />
          </div>
          <div class="pl-12px">
            <h3 class="text-18px font-semibold">
              {{ $t('page.home.greeting', { userName: authStore.userInfo.userName }) }}
            </h3>
            <p class="text-#999 leading-30px">欢迎使用图书管理系统，享受您的阅读时光</p>
          </div>
        </div>
      </ElCol>
      <ElCol :md="6" :sm="24">
        <ElSpace direction="horizontal" class="w-full justify-end" :size="24">
          <ElStatistic
            v-for="item in statisticData"
            :key="item.id"
            class="whitespace-nowrap text-center"
            :title="item.title"
            :value="item.value"
            :formatter="item.formatter"
            :value-style="{
              color: item.id === 1 && item.value > 0 ? '#f56c6c' : '#409EFF',
              fontSize: '18px',
              fontWeight: 'bold'
            }"
          />
        </ElSpace>
      </ElCol>
    </ElRow>
  </ElCard>
</template>

<style scoped></style>
