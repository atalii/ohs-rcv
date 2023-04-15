from dataclasses import dataclass

import csv
import sys

@dataclass
class Voter:
    """An ordered list of choices. Choices are stored in order with the first
    choice first and the last choice last."""

    choices: list[str]

    def transfer_vote(self):
        if len(self.choices) > 0:
            # Each election only has a few choices and only some voters
            # transfer their votes, so linear time complexity shouldn't matter
            # here. If it ever does, store choices in reverse order so that
            # vote transfers just involve popping the last element ((O(1)).
            self.choices.pop(0)
        else:
            return None

    @property
    def current_favorite(self) -> str:
        return self.choices[0]


@dataclass
class Election:
    voters: list[Voter]

    def elect(self) -> list[(str, int)]:
        """Run the election: Return the party's votes."""
        total_voter_count = len(self.voters)

        choices = self._get_choices()
        counted = [(len(voters), party) for party, voters in choices.items()]
        counted.sort(key=lambda k: k[0], reverse=True)

        # If, at this point, we have a majority, we're done. Otherwise, we
        # reallocate the least-favorite and recurse to try again.
        if counted[0][0] > total_voter_count / 2:
            return counted
        else:
            last_party = counted[-1][1]
            for voter in self.voters:
                if voter.current_favorite == last_party:
                    voter.transfer_vote()

            return self.elect()


    def _get_choices(self) -> dict[str, list[Voter]]:
        """Return the current election state with each voters' first choices."""
        votes = {}

        for voter in self.voters:
            vote = voter.current_favorite

            if vote is None:
                continue

            if vote not in votes:
                votes[vote] = [voter]
            else:
                votes[vote].append(voter)

        return votes

def _read_voters(sheet) -> list[Voter]:
    """Take a CSV reader and create the Voter list."""
    voters = []

    # Skip the first 18 columns, which contain data that aren't votes. Skip the
    # first row which contains headers.
    candidates, *votes = [row[17:] for row in sheet][1:]

    for row in votes:
        choices = [(int(choice), candidates[i]) for i, choice in enumerate(row) if choice.isdigit()]
        choices.sort(key=lambda k: k[0])

        choices = [cand for (choice, cand) in choices]

        if len(choices) > 0:
            voters.append(Voter(choices))

    return voters

if __name__ == '__main__':
    # Expect a CSV on stdin. See _read_voters for the format we expect. (This
    # is just what I got out of the qualtrics form I was sent, it may need to
    # be modified.)

    file = sys.stdin
    voter_doc = csv.reader(file)
    voters = _read_voters(voter_doc)

    print(Election(voters).elect())

