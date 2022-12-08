def process_filter(request, queryset, **kwargs):
    """
    process_filter(request, queryset,
                target1=(id, type, default),
                target2=(id, type, default),
                target3=(id, type, default),)
    """

    for target, (id, type_, default) in kwargs.items():
        data = request.GET.get(id, default)
        if not data:
            continue

        data = type_(data)
        queryset = queryset.filter(**{target: data})

    return queryset
    

def process_sorted(request, queryset, target, offset, limit):
    array_design_keyword = {
        "offset": 0, "limit": 10, "step": 1
    }

    for label, default, r, rdefault in target:
        data = request.GET.get(label, default)
        if not data:
            continue
        
        prefix = "-" if request.GET.get(r, rdefault) else ""

        queryset = queryset.order_by(f"{prefix}{data}")

    offset = request.GET.get("offset", offset)
    limit = request.GET.get("limit", limit)

    return queryset[offset : offset+limit]

# 날짜간의 개월 수 차이를 구하는 함수
def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

