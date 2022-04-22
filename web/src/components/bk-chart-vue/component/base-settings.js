/*
 * Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
 * Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
 * BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
 *
 * License for BK-LOG 蓝鲸日志平台:
 * --------------------------------------------------------------------
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 * documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial
 * portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
 * LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
 * NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
 */

export default {
  name: 'BaseSettings',
  props: {
    width: String,
    height: String,
    series: { type: Array, default: () => ([]) },
    legend: { type: Array, default: () => ([]) },
    animation: { type: Object, default: () => ({}) },
    yAxis: { type: Array, default: () => ([]) },
    labels: { type: Array, default: () => ([]) },
    title: { type: Object, default: () => ({}) },
    options: { type: Object, default: () => ({}) },
    responsive: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      chartColors: {
        red: 'rgb(255, 99, 132)',
        orange: 'rgb(255, 159, 64)',
        yellow: 'rgb(255, 205, 86)',
        green: 'rgb(75, 192, 192)',
        blue: 'rgb(54, 162, 235)',
        purple: 'rgb(153, 102, 255)',
        grey: 'rgb(201, 203, 207)',
      },
      containerNode: null,
      container: null,
      context: null,
      instance: null,
      type: '',
      plugins: {
        zoom: {
          // Container for pan options
          pan: {
            // Boolean to enable panning
            enabled: false,
            mode: 'x',

            rangeMin: {
              // Format of min pan range depends on scale type
              x: null,
              y: null,
            },
            rangeMax: {
              // Format of max pan range depends on scale type
              x: null,
              y: null,
            },
            speed: 20,

            // Minimal pan distance required before actually applying pan
            threshold: 10,

            // Function called while the user is panning
            onPan: () => {
              console.log('I\'m panning!!!');
            },
            // Function called once panning is completed
            onPanComplete: () => {
              console.log('I was panned!!!');
            },
          },

          // Container for zoom options
          zoom: {
            // Boolean to enable zooming
            enabled: true,

            // Enable drag-to-zoom behavior
            drag: false,
            mode: 'xy',

            rangeMin: {
              // Format of min zoom range depends on scale type
              x: null,
              y: null,
            },
            rangeMax: {
              // Format of max zoom range depends on scale type
              x: null,
              y: null,
            },

            // Speed of zoom via mouse wheel
            // (percentage of zoom on a wheel event)
            speed: 0.1,

            // On category scale, minimal zoom level before actually applying zoom
            sensitivity: 3,

            // Function called while the user is zooming
            onZoom: () => {
              console.log('I\'m zooming!!!');
            },
            // Function called once zooming is completed
            onZoomComplete: () => {
              console.log('I was zoomed!!!');
            },
          },
        },
      },
    };
  },
  methods: {
    update() {
      this.instance.datasets = this.chartConfig;
      this.instance.labels = this.yAxis;
      this.instance.update();
    },
    init(node) {
      this.containerNode = node;
      this.container = this.containerNode.querySelector('canvas');
      if (!this.container) {
        this.container = document.createElement('canvas');
        if (this.width) {
          this.container.style.width = this.width;
        }

        if (this.height) {
          this.container.style.height = this.height;
        }

        this.containerNode.append(this.container);
      }

      this.context = this.container.getContext('2d');
    },
  },
};
