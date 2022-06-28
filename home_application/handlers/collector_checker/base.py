# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
License for BK-LOG 蓝鲸日志平台:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
We undertake not to change the open source license (MIT license) applicable to the current version of
the project delivered to anyone in the future.
"""
import json
from home_application.constants import CHECK_STORIES


class StoryCollection(object):
    name = ""
    stories = {}

    def register(self, story):
        self.stories[story.name] = story

    def run(self):
        story_result_list = []
        for story_name in CHECK_STORIES:
            if not self.stories.get(story_name):
                break
            story = self.stories[story_name]
            story_m = story.check()
            story_result_list.append(story_m)
            if story_m.has_problem:
                break
        return story_result_list

    def __str__(self):
        return self.__class__.name


sc = StoryCollection()


def register_story(*args, **kwargs):
    def register(cls):
        story = cls(*args, **kwargs)
        story.steps = []
        sc.register(story)
        return cls

    return register


def register_step(story_cls):
    story = None
    for s in sc.stories:
        if sc.stories[s].__class__ == story_cls:
            story = sc.stories[s]
            break
    else:
        raise OSError("can't find story: {}".format(story_cls))

    def register(cls):
        step = cls(story)
        story.steps.append(step)
        return cls

    return register


class StepReport(object):
    def __init__(self, step, info: list = None, warning: list = None, error: list = None):
        self.step = step
        self.name = step.name
        self.info = info if info else []
        self.warning = warning if warning else []
        self.error = error if warning else []

    def has_problem(self):
        return self.error != []

    def __str__(self):
        return json.dumps(
            {"step_name": self.step.name, "info": self.info, "warning": self.warning, "error": self.error},
            ensure_ascii=False,
        )


class StoryReport(object):
    def __init__(self, story, info: list = None, warning: list = None, error: list = None):
        self.story = story
        self.name = story.name
        self.info = info if info else []
        self.warning = warning if warning else []
        self.error = error if warning else []

    def has_problem(self):
        return self.error != []

    def add_step_report(self, step_report):
        self.info.extend(step_report.info)
        self.warning.extend(step_report.warning)
        self.error.extend(step_report.error)

    def __str__(self):
        return json.dumps(
            {"story_name": self.story.name, "info": self.info, "warning": self.warning, "error": self.error},
            ensure_ascii=False,
        )


class BaseStory(object):
    name = ""
    steps = []

    def check(self):
        story_r = StoryReport(self)
        for i, step in enumerate(self.steps):
            story_r.name = f"步骤{i+1}: {story_r.name}"
            try:
                step_r = step.check()
            except Exception as err:
                step_r = StepReport(self)
                step_r.error.append(f"步骤{i+1}: [{self.name}] [{step_r.name}] 异常: {err}")
            story_r.add_step_report(step_r)
        return story_r

    def __str__(self):
        return self.__class__.name


class BaseStep(object):
    name = ""

    def __init__(self, story):
        self.story = story

    def check(self):
        raise NotImplementedError

    def __str__(self):
        return self.name
