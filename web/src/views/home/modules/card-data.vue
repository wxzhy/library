<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { createReusableTemplate } from '@vueuse/core';
import { $t } from '@/locales';
import { fetchStatistics } from '@/service/api';

defineOptions({ name: 'CardData' });

interface CardData {
  key: string;
  title: string;
  value: number;
  unit: string;
  color: {
    start: string;
    end: string;
  };
  icon: string;
}

const siteStats = ref<Api.SystemManage.Statistics>({
  total_users: 0,
  total_books: 0,
  total_borrows: 0,
  active_borrows: 0,
  overdue_borrows: 0
});

const cardData = computed<CardData[]>(() => [
  {
    key: 'totalUsers',
    title: '总用户数',
    value: siteStats.value.total_users,
    unit: '',
    color: {
      start: '#ec4786',
      end: '#b955a4'
    },
    icon: 'ant-design:user-outlined'
  },
  {
    key: 'totalBooks',
    title: '图书总数',
    value: siteStats.value.total_books,
    unit: '',
    color: {
      start: '#865ec0',
      end: '#5144b4'
    },
    icon: 'ant-design:book-outlined'
  },
  {
    key: 'activeBorrows',
    title: '当前借阅',
    value: siteStats.value.active_borrows,
    unit: '',
    color: {
      start: '#56cdf3',
      end: '#719de3'
    },
    icon: 'ant-design:read-outlined'
  },
  {
    key: 'overdueBorrows',
    title: '逾期图书',
    value: siteStats.value.overdue_borrows,
    unit: '',
    color: {
      start: '#fcbc25',
      end: '#f68057'
    },
    icon: 'ant-design:warning-outlined'
  }
]);

interface GradientBgProps {
  gradientColor: string;
}

const [DefineGradientBg, GradientBg] = createReusableTemplate<GradientBgProps>();

function getGradientColor(color: CardData['color']) {
  return `linear-gradient(to bottom right, ${color.start}, ${color.end})`;
}

// 获取站点统计信息
async function getSiteStatistics() {
  try {
    const { data } = await fetchStatistics();
    if (data) {
      siteStats.value = data;
    }
  } catch (error) {
    console.error('获取站点统计失败:', error);
  }
}

onMounted(() => {
  getSiteStatistics();
});
</script>

<template>
  <ElCard class="card-wrapper">
    <!-- define component start: GradientBg -->
    <DefineGradientBg v-slot="{ $slots, gradientColor }">
      <div class="rd-8px px-16px pb-4px pt-8px text-white" :style="{ backgroundImage: gradientColor }">
        <component :is="$slots.default" />
      </div>
    </DefineGradientBg>
    <!-- define component end: GradientBg -->
    <ElRow :gutter="16">
      <ElCol v-for="item in cardData" :key="item.key" :lg="6" :md="12" :sm="24" class="my-8px">
        <GradientBg :gradient-color="getGradientColor(item.color)" class="flex-1">
          <h3 class="text-16px">{{ item.title }}</h3>
          <div class="flex justify-between pt-12px">
            <SvgIcon :icon="item.icon" class="text-32px" />
            <CountTo
              :prefix="item.unit"
              :start-value="0"
              :end-value="item.value"
              class="text-30px text-white dark:text-dark"
            />
          </div>
        </GradientBg>
      </ElCol>
    </ElRow>
  </ElCard>
</template>

<style scoped></style>
