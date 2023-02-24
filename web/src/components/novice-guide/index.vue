<!--
  - Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
  - Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
  - BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
  -
  - License for BK-LOG 蓝鲸日志平台:
  - -------------------------------------------------------------------
  -
  - Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
  - documentation files (the "Software"), to deal in the Software without restriction, including without limitation
  - the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
  - and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  - The above copyright notice and this permission notice shall be included in all copies or substantial
  - portions of the Software.
  -
  - THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
  - LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
  - NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  - WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  - SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
  -->

<template>
  <transition name="guide-fade">
    <div v-if="!isDone && stepList.length" ref="wraper" class="novice-guide">
      <StepBox
        ref="tip"
        :placement="placement"
        :tip-styles="tipStyles"
        v-if="!isShowFinisheDialog && !isShowStopDialog"
      >
        <div slot="title">
          {{ currentStep.title }}（{{ currentStepNum }}/{{ stepList.length }}）
        </div>
        <div slot="content">{{ currentStep.content }}</div>
        <template slot="action">
          <template v-if="!isLast">
            <div class="action-text" @click="handleStepChange('stop')">{{ $t('跳过') }}</div>
            <div class="action-btn" @click="handleStepChange('next')">{{ $t('下一步') }}</div>
          </template>
          <div v-else class="action-btn" @click="handleStepChange('finish')">{{ $t('完成') }}</div>
        </template>
      </StepBox>

      <!-- <div v-if="isShowFinisheDialog" class="guide-finished-box">
        <div class="wraper">
          <div class="flag">
            <i class="bk-icon icon-check-1" />
          </div>
          <div style="font-size: 24px; line-height: 31px; color: #313238">恭喜完成学习!</div>
          <div style="margin-top: 8px; font-size: 14px; line-height: 19px; color: #979BA5">
            {{ doneCountTime }} 秒后弹窗自动消失
          </div>
          <div style="margin-top: 20px">
            <span style="font-size: 14px; line-height: 19px; color: #3480FF; cursor: pointer" @click="handleDone">
              立即体验
            </span>
          </div>
        </div>
      </div> -->
      <!-- <div v-if="isShowStopDialog" class="guide-stop-box">
        <div class="wraper">
          <div style="font-size: 24px; line-height: 31px; color: #313238">确认跳过学习？</div>
          <div style="margin-top: 27px; font-size: 14px; line-height: 19px; color: #63656E">
            跳过此次学习，你可点击页面右上角的帮助指引，再次发起学习。
          </div>
          <div style="margin-top: 22px;">
            <img :src="helpImg" style="width: 157px; height: 157px" />
          </div>
          <div style="margin-top: 27px">
            <bk-button theme="primary" class="mr10" @click="handleDone">确定</bk-button>
            <bk-button @click="handleCancelStop">取消</bk-button>
          </div>
          <div class="cancal-btn" @click="handleCancelStop">
            <i class="bk-icon icon-close" />
          </div>
        </div>
      </div> -->
    </div>
  </transition>
</template>

<script>
import _ from 'lodash';
import StepBox from '../step-box/index.vue';
// import cookie from 'cookie';

// const CACHE_KEY = 'lesscode_supermen';

export default {
  name: '',
  components: {
    StepBox,
  },
  props: {
    guidePage: {
      type: String,
      required: '',
    },
    data: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      isShowFinisheDialog: false,
      isShowStopDialog: false,
      // isDone: cookie.parse(document.cookie).hasOwnProperty(CACHE_KEY),
      isDone: false,
      currentStepIndex: 0,
      currentStep: {},
      tipStyles: {},
      placement: '',
      doneCountTime: 3,
    };
  },
  computed: {
    currentStepNum() {
      return this.currentStepIndex + 1;
    },
    stepList() {
      return this.data?.step_list || [];
    },
    isInitStep() {
      return this.data?.current_step || 0;
    },
    isLast() {
      return this.currentStepIndex === this.stepList.length - 1;
    },
  },
  created() {
    this.helpImg = '';
    window.__lesscodeEditPageGuide = this;
    this.currentStepIndex = this.isInitStep;
    this.isDone = this.isInitStep === this.stepList.length;
  },
  mounted() {
    this.init();
    window.addEventListener('resize', this.handleReize);
  },
  beforeDestroy() {
    this.clearActive();
    this.$refs.wraper && this.$refs.wraper.parentNode.removeChild(this.$refs.wraper);
    window.removeEventListener('resize', this.handleReize);
  },
  methods: {
    /**
     * 指引初始化
     */
    init() {
      if (!this.isDone) {
        document.body.appendChild(this.$refs.wraper);
        this.activeStep();
      }
    },
    /**
     * 外部调用，开始指引
     */
    start() {
      this.isDone = false;
      this.isShowFinisheDialog = false;
      this.isShowStopDialog = false;
      this.currentStepIndex = 0;
      this.doneCountTime = 3;
      // document.cookie = cookie.serialize(CACHE_KEY, Date.now(), {
      //   expires: new Date(Date.now() - 1),
      //   path: '/',
      // });
      this.$nextTick(() => {
        this.init();
      });
    },
    /**
     * 步骤切换时激活目标步骤
     */
    activeStep() {
      this.$nextTick(() => {
        const windowWidth = window.innerWidth;
        const windowHieght = window.innerHeight;
        const currentStep = this.stepList[this.currentStepIndex];
        const $stepTarget = document.querySelector(currentStep.target);
        $stepTarget.classList.add('guide-highlight');
        if (typeof this.currentStep.leave === 'function') {
          this.currentStep.leave();
        }
        if (typeof currentStep.entry === 'function') {
          currentStep.entry();
        }
        setTimeout(() => {
          const {
            top: targetTop,
            right: targetRight,
            bottom: targeBottom,
            left: targetLeft,
            width: targetWidth,
          } = $stepTarget.getBoundingClientRect();
          const {
            width,
            height,
          } = this.$refs.tip.$el.getBoundingClientRect();

          let placement = 'left';
          if (width > height && targeBottom < 0.3 * windowHieght) {
            placement = targeBottom > 0.5 * windowHieght ? 'top' : 'bottom';
          } else {
            placement = targetLeft > 0.5 * windowWidth ? 'left' : 'right';
          }

          let styles = {};

          if (placement === 'bottom') {
            styles = {
              top: `${targeBottom + 10}px`,
              left: `${targetLeft + (targetWidth - width) / 2}px`,
            };
          } else if (placement === 'top') {
            styles = {
              top: `${windowHieght - targetTop - height - 10}px`,
              left: `${targetLeft + (targetWidth - width) / 2}px`,
            };
          } else if (placement === 'left') {
            styles = {
              top: `${targetTop}px`,
              right: `${windowWidth - targetLeft + 10}px`,
            };
          } else if (placement === 'right') {
            styles = {
              top: `${targetTop}px`,
              left: `${targetRight + 10}px`,
            };
          }
          this.currentStep = Object.freeze(currentStep);
          this.tipStyles = Object.freeze(styles);
          this.placement = placement;
        });
      });
    },
    /**
     * 清空所有步骤的激活状态
     */
    clearActive() {
      document.body.querySelectorAll('.guide-highlight').forEach((el) => {
        el.classList.remove('guide-highlight');
      });
    },
    /**
     * 完成指引
     */
    doneGudie() {
      // document.cookie = cookie.serialize(CACHE_KEY, Date.now(), {
      //   expires: new Date(Date.now() + 31104000000),
      //   path: '/',
      // });
      this.isDone = true;
      if (this.currentStep && typeof this.currentStep.leave === 'function') {
        this.currentStep.leave();
      }
      setTimeout(() => {
        this.$refs.wraper && this.$refs.wraper.parentNode.removeChild(this.$refs.wraper);
      });
    },
    /**
     * 窗口缩放
     */
    handleReize: _.throttle(function () {
      if (!this.isDone) {
        this.activeStep();
      }
    }, 100),
    /**
     * 跳过指引确认操作
     */
    handleStop() {
      // this.isShowStopDialog = true;
      this.clearActive();
      this.handleDone();
    },
    /**
     * 取消跳过指引
     */
    handleCancelStop() {
      this.isShowStopDialog = false;
      this.activeStep();
    },
    /**
     * 切换步骤
     */
    handleNext() {
      this.currentStepIndex += 1;
      this.clearActive();
      this.activeStep();
    },
    /**
     * 结束指引确认操作
     */
    handleFinish() {
      this.clearActive();
      this.doneGudie();
      // this.isShowFinisheDialog = true;
      // const countdown = () => {
      //   setTimeout(() => {
      //     this.doneCountTime -= 1;
      //     if (this.doneCountTime > 0) {
      //       countdown();
      //     } else {
      //       this.doneGudie();
      //     }
      //   }, 1000);
      // };
      // countdown();
    },
    /**
     * 完成指引
     */
    handleDone() {
      this.doneGudie();
    },
    /**
     * 完成指引
     */
    handleStepChange(step) {
      const curStep = ['stop', 'finish'].includes(step) ? this.stepList.length : this.currentStepIndex + 1;

      this.$http.request('meta/updateUserGuide', { data: { [this.guidePage]: curStep } }).then(() => {
        step === 'next' ? this.handleNext() : step === 'finish' ? this.handleFinish() : this.handleStop();
      })
        .catch((e) => {
          console.warn(e);
        });
    },
  },
};
</script>

<style lang='scss'>
  body {
    *.guide-highlight {
      /* stylelint-disable-next-line declaration-no-important */
      opacity: 1 !important;

      /* stylelint-disable-next-line declaration-no-important */
      z-index: 100001 !important;
      background: #fff;

      /* stylelint-disable-next-line declaration-no-important */
      pointer-events: none !important;
    }
  }

  .novice-guide {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    z-index: 100000;
    background: rgba(0,0,0,.6);

    .guide-finished-box {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);

      .wraper {
        width: 400px;
        height: 210px;
        padding-top: 74px;
        text-align: center;
        background: #fff;
        border-radius: 2px;

        .flag {
          position: absolute;
          top: 0;
          left: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          width: 86px;
          height: 86px;
          font-size: 55px;
          color: #fff;
          border: 13px solid #dcffe2;
          border-radius: 50%;
          background: #2dcb56;
          transform: translate(-50%, -27px);

          &:after {
            content: '';
            position: absolute;
          }
        }
      }
    }

    .guide-stop-box {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);

      .wraper {
        width: 500px;
        height: 370px;
        padding-top: 25px;
        text-align: center;
        border-radius: 2px;
        background: #fff;

        .cancal-btn {
          position: absolute;
          top: 5px;
          right: 5px;
          width: 26px;
          height: 26px;
          font-weight: 700;
          font-size: 22px;
          color: #979ba5;
          line-height: 26px;
          text-align: center;
          border-radius: 50%;
          cursor: pointer;

          &:hover {
            background-color: #f0f1f5;
          }
        }
      }
    }
  }

  .guide-fade-leave-active {
    transition: visibility .15s linear, opacity .1s linear;
  }

  .guide-fade-leave-to {
    opacity: 0;
    visibility: hidden;
  }
</style>
