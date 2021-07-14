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

const qs = require('qs');

class HttpRequst {
  constructor(axios, options) {
    this.mockJson = null;
    this.services = null;
    this.axiosInstance = axios;
    this.options = options;
  }

  request(service, options = {}, config = {}) {
    const _options = Object.assign({}, this.options, options);
    if (_options.mock) {
      this.__initMockJson(_options);
      const mockData = this.__getMockResult(service, options);
      if (mockData !== null) {
        return Promise.resolve(mockData);
      }
    }

    this.__initServices(_options);
    const _service = this.__getHttpService(service, _options);
    return this.__resolveSericeRequset(_service, _options, config);
  }

  __resolveSericeRequset(service, options, config) {
    if (typeof service.url === 'string') {
      let _service = this.__formatService(service, options);
      _service = Object.assign({}, { method: options.method || 'get' }, _service);
      if (service.callback && typeof service.callback === 'function') {
        return this.__axios(_service.url, _service.method, options.data, options.query, options.ext, config)
          .then(res => service.callback(res, options));
      }
      return this.__axios(_service.url, _service.method, options.data, options.query, options.ext, config);
    }
    if (Array.isArray(service.url)) {
      const requests = [];
      service.url.forEach((url) => {
        if (typeof url === 'string') {
          const _url = this.__formatUrl(url, options);
          requests.push(this.__axios(_url, service.method
            || options.method
            || 'get', options.data, options.query, options.ext, config));
        } else {
          let _service = this.__formatService(url, options);
          _service = Object.assign({}, { method: options.method || 'get' }, _service);
          requests.push(this.__axios(_service.url, _service.method, options.data, options.query, options.ext, config));
        }
      });
      if (service.callback && typeof service.callback === 'function') {
        return Promise.all(requests).then(res => service.callback(res, options));
      }
      return Promise.all(requests);
    }
    return Promise.reject(new Error('Url Resolve Error'));
  }

  __getHttpService(service, options) {
    const splitor = this.__getSericeSplitor(service);
    let _service = splitor[1]
      ? this.services[splitor[0]][splitor[1]]
      : this.services[splitor[0]];
    if (typeof _service === 'function') {
      _service = _service(service, options);
    }
    return _service;
  }

  __getSericeSplitor(service) {
    return service.split('/').filter(f => f);
  }

  __getMockResult(service, options) {
    if (this.mockJson) {
      const splitor = this.__getSericeSplitor(service);
      let mock = splitor[1]
        ? this.mockJson[splitor[0]]
          ? this.mockJson[splitor[0]][splitor[1]]
          : null
        : this.mockJson[splitor[0]];
      if (typeof mock === 'function') {
        mock = mock(service, options);
      }

      const res = options.manualSchema ? mock : { data: mock, result: true, code: 0 };

      if (options.timeout) {
        return new Promise((resolve) => {
          setTimeout(() => {
            resolve(res);
          }, options.timeout);
        });
      }

      return res;
    }
    return null;
  }

  __formatService(service, option) {
    const _service = JSON.parse(JSON.stringify(service));
    const { url } = _service;
    _service.url = this.__formatUrl(url, option);
    return _service;
  }

  __formatUrl(url, option) {
    if (option && option.params) {
      const matchs = url.match(/:(_|\d|_|[a-z])+/gi);
      if (matchs && matchs.length) {
        matchs.forEach((match) => {
          const key = match.replace(/^:/, '');
          const param = option.params[key];
          url = url.replace(match, param);
        });
      }
    }
    return url;
  }

  __initMockJson(_options) {
    if (_options.mock && _options.mockList) {
      if (!this.mockJson) {
        this.mockJson = _options.mockList;
      }
    }
  }

  __initServices(_options) {
    if (_options.serviceList) {
      if (!this.services) {
        this.services = _options.serviceList;
      }
    }
  }

  __axios(url, method, data, query, ext, config) {
    const param = Object.assign({}, {
      url,
      method,
      data,
      params: query,
      paramsSerializer(params) {
        return qs.stringify(params, { arrayFormat: 'repeat' });
      },
    }, ext || {}, config);
    return this.axiosInstance(param);
  }
}

export default HttpRequst;
