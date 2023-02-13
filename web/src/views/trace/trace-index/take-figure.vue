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
  <div class="TakeDemo">
    <div class="check">
      <div>
        <span class="chunkclor Auqamarin"></span>
        <span>0-20</span>
      </div>
      <div>
        <span class="chunkclor MediumSpringGreen"></span>
        <span>21-40</span>
      </div>
      <div>
        <span class="chunkclor LightYellow"></span>
        <span>41-70</span>
      </div>
      <div>
        <span class="chunkclor LightGoldenrodYellow"></span>
        <span>71-100</span>
      </div>
      <div>
        <span class="chunkclor Beige"></span>
        <span>101-150</span>
      </div>
      <div>
        <span class="chunkclor Yellow"></span>
        <span>151-200</span>
      </div>
      <div>
        <span class="chunkclor GoldEnrod"></span>
        <span>201-250</span>
      </div>
      <div>
        <span class="chunkclor Orange"></span>
        <span>251-300 </span>
      </div>
      <div>
        <span class="chunkclor DarkOrange"></span>
        <span>301-500</span>
      </div>
      <div>
        <span class="chunkclor OrangeRed"></span>
        <span>500+(ms)</span>
      </div>
    </div>
    <div class="row" v-for="x in datasets" :key="x.label">
      <div class="column" :title="x.label">{{x.label}}</div>
      <span></span>
      <div
        v-for="item in x.data"
        class="chunk"
        :key="item.label"
        :class="item.value < 21 ?
          'Auqamarin' : item.value < 41 ?
            'MediumSpringGreen' : item.value < 71 ?
              'LightYellow' : item.value < 101 ?
                'LightGoldenrodYellow' :
                item.value < 151 ?
                  'Beige' : item.value < 201 ?
                    'Yellow' : item.value < 251 ?
                      'GoldEnrod' : item.value < 301 ?
                        'Orange' : item.value < 501 ?
                          'DarkOrange' : 'OrangeRed'"
        @mouseenter="handleEnter($event,item)"
        @mouseleave="handleLeave">
      </div>
    </div>
    <div class="abscissa">
      <div class="column"></div>
      <span></span>
      <div v-for="item in abscissa" class="chunk" :key="item.theTime">
        {{item.theTime}}
        <div>{{item.theDate}}</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Takefigure',
  props: {
    conum: {
      type: Object,
      default: () => {},
    },
  },
  data() {
    return {
      abscissa: [],
      datasets: [],
    };
  },
  watch: {
    conum() {
      this.conumType();
    },
  },
  created() {
    this.conumType();
  },
  methods: {
    handleEnter(e, val) {
      this.instance = this.$bkPopover(e.target, {
        content: `<div>${this.$t('耗时：')}${val.value}</div><div>${this.$t('时间：')}${val.label}</div><div>${this.$t('数量：')}${val.count}</div>`,
        arrow: true,
        placement: 'top',
      });
      this.instance.show(1000);
    },
    handleLeave() {
      this.instance && this.instance.destroy(true);
    },
    conumType() {
      const labels = [];
      let lists = [];
      let day = '';
      let data;
      let x = 5;
      let y = 2;
      if (this.conum.labels.length > 120) {
        x = 20;
        y = 9;
      }
      this.conum.labels.forEach((item, index) => {
        // 每五个点取一个横坐标
        if (item.length > 10) {
          lists = item.split(' ');
          data = {
            theDate: day === lists[0] ? '' : lists[0],
            theTime: lists[1],
          };
          day = lists[0];
        } else {
          data = {
            theDate: '',
            theTime: item,
          };
        }
        if (index % x === y) {
          labels.push(data);
        }
      });
      this.abscissa = labels;
      this.datasets = this.conum.datasets;
      // 删除第一个value为0的点
      this.datasets.forEach((item) => {
        item.data.splice(0, 1);
      });
    },
  },
};
</script>

<style scoped lang="scss">
  .TakeDemo {
    .chunk-border {
      border-top: 1px solid rgba(231, 232, 236, .8);
    }

    .check {
      width: 100%;
      display: flex;
      justify-content: center;
      margin-bottom: 20px;

      div {
        margin-right: 20px;
        line-height: 20px;
      }

      .chunkclor {
        display: inline-block;
        width: 10px;
        height: 10px;
        margin-right: 5px;
      }
    }

    .abscissa {
      display: flex;
      line-height: 20px;
      margin-top: -2px;

      .column {
        width: 150px;
        flex-shrink: 0;
        text-overflow: ellipsis;
      }

      .chunk {
        border-top: 1px solid rgba(231, 232, 236, .8);
        width: 100%;
        text-align: center;
        font-size: 12px;
      }

      .span {
        width: 6px;
        display: inline-block;
        border-bottom: 1px solid rgba(231, 232, 236, .8);
        flex-shrink: 0;
      }
    }
  }

  .row {
    display: flex;
    height: 22px;

    div:last-child {
      border-right: 1px solid rgba(196,198,204,.8);
    }

    .chunk {
      width: 100%;
      height: 21px;
      line-height: 48px;
      text-align: center;
      border-left: 1px solid  rgba(196,198,204,.8);
    }

    .column {
      width: 150px;
      flex-shrink: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      text-align: right;
      background-color: #fff;
      line-height: 22px;
      font-size: 14px;
    }

    span {
      display: inline-block;
      width: 6px;
      height: 44px;
      flex-shrink: 0;
      border-top: 1px solid rgba(231, 232, 236, .8);
    }
  }

  .Auqamarin {
    background-color: rgba(0, 250, 0, .2);
  }

  .MediumSpringGreen {
    background-color: rgba(0, 250, 0, .3);
  }

  .LightYellow {
    background-color: #ffffe0;
  }

  .LightGoldenrodYellow {
    background-color: #fafad2;
  }

  .Beige {
    background-color: #f5f5dc;
  }

  .Yellow {
    background-color: #ff0;
  }

  .GoldEnrod {
    background-color: #ffd700;
  }

  .Orange {
    background-color: #ffa500;
  }

  .DarkOrange {
    background-color: #ff8c00;
  }

  .OrangeRed {
    background-color: #f07c7d;
  }
</style>
