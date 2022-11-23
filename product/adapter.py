from allauth.account.adapter import DefaultAccountAdapter

class MemberAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, member, form, commit=False):
        member = super().save_user(request, member, form, commit)
        data = form.cleaned_data
        member.nickname = data.get('nickname')
        member.profile = data.get('profile')
        member.profile_image = data.get('profile_image')
        member.save()
        return member