"""
Copyright (C) 2017 Planview, Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


def should_run(parameter_tags, test_tags, browser=None, exclusion_tags=None):
    default_exclusion_tags = ['inactive', 'not active']
    if browser:
        # Make browser case insensitive
        default_exclusion_tags += ['not '+browser.lower(),
                                   'not '+browser.title(),
                                   'not '+browser.upper()]
    if exclusion_tags:
        default_exclusion_tags += exclusion_tags

    run = False

    # Should test be excluded?
    for tag in test_tags:
        if {'~' + tag, 'not ' + tag}.intersection(parameter_tags) or \
                        tag in default_exclusion_tags:
            return run

    # Any common items?
    if set(test_tags).intersection(parameter_tags) or 'all' in parameter_tags:
        run = True

    # Check for filter(s), ie. tag1+tag2
    elif any([True if "+" in tag else False for tag in parameter_tags]):
        for tag in parameter_tags:
            filtered_tags = tag.split('+')
            if set(filtered_tags).issubset(set(test_tags)):
                run = True
                break

    return run
