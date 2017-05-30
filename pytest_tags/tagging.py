AWAITING_FIX = "awaiting_fix"


class TagsParameter(object):
    """
    Container for the entered parameter tags.
    Decides whether a test should be picked up based on the test, class,
    and module tags.
    """

    def __init__(self, browser, parameter_tags):
        """
        @browser, eg. 'firefox', 'chrome', 'ie9'
        @parameter_tags, list of tags to run
        """
        self._excluded_tags = ['active', AWAITING_FIX]
        if browser:
            self._excluded_tags.append(browser)
        self._parameter_tags = TagsCollection.build_tags_list(parameter_tags)

    def should_pick_up(self, tags):
        prep_tags = TagsCollection.prep_tags(tags)

        for tag in prep_tags:
            # If tag is set to 'not active', don't run the test
            # If tag is awaiting fix, don't run the test
            # If current env is excluded (eg. 'not reltest'), don't run test
            # If current browser is excluded (eg. 'not ie8'), don't run test
            if tag.name in self._excluded_tags and not tag.is_positive:
                return False

        should_run = False
        for tag in prep_tags:
            # Check tags
            for param_tag in self._parameter_tags:
                # If either the parameter tag or test tag is set to False
                # (eg. 'not sierra'), don't run the test
                if param_tag.name == tag.name and \
                        (not param_tag.is_positive or not tag.is_positive):
                    return False
                # If the user has filtered tags using + (ie. sierra+snap),
                # only run test that corresponds to both tags
                # The 'and not should_run' needs some explaining:
                # It's a fix for when you have more than one set of
                # +-combinations ie. tag1+tag2, tag3+tag4
                # if tag1+tag2 sets should_run to True, we've already
                # determined that the test should be run, hence we
                # can skip the other combinations, but we don't want to skip
                # the entire function, in case there are any 'not' tags.
                elif '+' in param_tag.name and not should_run:
                    for name in param_tag.name.split('+'):
                        if Tag(name, True) in prep_tags:
                            should_run = True
                        else:
                            should_run = False
                            break
                # If we have a match and both are set to positive, run the test
                elif param_tag == tag:
                    should_run = True

        # If none of the above checks caught anything,
        # the <should_run> determines if the test gets picked up
        if self._parameter_tags:
            return should_run

        # Or if no tags where specified as parameters (eg. -t),
        # we run the test (this will run ALL tests)
        return True


class TagsCollection(object):
    """
    Class with static methods for tags-manipulation.
    """

    @staticmethod
    def build_tags_list(tags):
        """
        Convert a list of tags type<string> to a list of tag-objects <Tag>

        :param tags: list of tags type<string>
        :return: list of tags type<Tag>
        """
        tags_list = []
        for tag in tags:
            if tag.startswith("not "):
                # Skip the 'not ' in the name, and set is_positive to False
                tags_list.append(Tag(tag[4:].lower(), False))
            elif tag.startswith("~"):
                tags_list.append(Tag(tag[1:].lower(), False))
            elif tag == AWAITING_FIX:
                tags_list.append(Tag(tag.lower(), False))
            else:
                tags_list.append(Tag(tag.lower(), True))

        return tags_list

    @staticmethod
    def prep_tags(tags):
        """
        Prepares tags by removing dupes and sorting.
        NOTE: Any tag with the prefix 'not' takes precedence!
        This is done by sorting the list of tags with the sorting-key being
        the tuple of tag.name and tag.is_positive.

        Example

            tag object is represented here as name.is_positive
            tags = ['snap.true', 'ie8.false', 'sierra.true', 'ie8.true']

        Sorted generates: ['ie8.false', 'ie8.true', 'sierra.true', 'snap.true']
        The sort-function always puts the x.false before x.true.

        :param tags: list of tags type<string>
        :return: list of prepped tags
        """
        # Sort the list based on tag name and is_positive, ascending order
        # 'not ' tags (is_positive = False) comes before positive tags.
        # Because False < True
        tags.sort(key=lambda a: (a.name, a.is_positive))

        # Remove duplicates (eg. every second, third,...  occurrence of a tag,
        # and since 'not' tags (is_positive = False) comes before positive tags
        # the 'not ' tag is kept, and all others considered duplicates.
        # Hence 'not ' tags gets precedence.
        return remove_dupes(tags, Tag.__hash__)


def remove_dupes(seq, func):
    seen = {}
    result = []
    for item in seq:
        marker = func(item)
        if marker not in seen:
            seen[marker] = 1
            result.append(item)
    return result


class Tag(object):
    def __init__(self, name, is_positive):
        self.name = name
        self.is_positive = is_positive

    def __str__(self):
        tag = self.name if not self.is_positive else self.name
        return 'not {}'.format(tag)

    def __eq__(self, other):
        if isinstance(other, Tag):
            return self.name == other.name and \
                   self.is_positive == other.is_positive
        else:
            return False

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.__repr__())
