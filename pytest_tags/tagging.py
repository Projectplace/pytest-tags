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
    for tag in default_exclusion_tags:
        if tag in test_tags:
            return run

    # Any common items?
    if set(test_tags).intersection(parameter_tags) \
            or 'all' in parameter_tags:
        run = True

    # Check for filter(s), ie. tag1+tag2
    else:
        filtered_tags = []
        for tag in parameter_tags:
            if '+' in tag:
                filtered_tags += tag.split('+')

        if len(test_tags) > 1 and \
                all(tag in filtered_tags for tag in test_tags):
            run = True
        else:
            run = False

    # Now check for other exclusions
    if run:
        for tag in test_tags:
            if {'~'+tag, 'not '+tag}.intersection(parameter_tags):
                run = False
                break

    return run
