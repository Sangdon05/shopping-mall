# 환경 설정

## Ruff (선택)

동일된 코드 형태를 유지하기 위해 Ruff 적용. 별도의 규칙 정의하지 않고 기본 설정으로 사용하였다.

[Ruff 설치 참고](https://docs.astral.sh/ruff/installation/)

## .env

Supabase URL, ANON_KEY 필수 (.env.sample을 복사하여 실제값 입력)

```
SUPABASE_URL=
SUPABASE_PUBLISHABLE_KEY=
SUPABASE_ANON_KEY=
```

# Supabase

## DB Scheme

```sql
create table user_details (
  id uuid primary key default gen_random_uuid(),
  type text default 'BUYER' check (type in ('SELLER', 'BUYER')) not null,
  cellphone text not null,
  zipcode text not null,
  address text not null,
  address_sub text,
  created_at timestamptz default now() not null,
  modified_at timestamptz,
  deleted_at timestamptz
);


create table products (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  description text,
  price int default 0 not null check(price >= 0),
  seller_id uuid references auth.users(id) not null,
  created_at timestamptz default now() not null,
  modified_at timestamptz,
  deleted_at timestamptz
);

create table orders (
  id uuid primary key default gen_random_uuid(),
  order_no text unique not null default generate_date_string(),
  order_name text not null,
  order_email text not null,
  order_phone text not null,
  receiver_name text not null,
  receiver_phone text not null,
  zipcode text not null,
  address text not null,
  address_sub text,
  delivery_memo text,
  total_price int not null check(total_price >= 0),
  order_status text default 'READY' check (order_status in ('READY', 'ORDER', 'IN_CASH', 'PREPARE', 'ON_DELIVERY', 'DONE_DELIVERY')) not null,
  created_at timestamptz default now() not null,
  modified_at timestamptz,
  deleted_at timestamptz,
  user_id uuid references auth.users(id) not null
);

create table order_items (
  id uuid primary key default gen_random_uuid(),
  order_id uuid references orders(id) not null,
  product_id uuid references products(id) not null,
  item_name text not null,
  price int not null,
  quantity int check (quantity >= 1) not null,
  created_at timestamptz default now() not null,
  modified_at timestamptz,
  deleted_at timestamptz
);
```

## 주문 번호 생성

```sql
create or replace function generate_date_string()
returns text
language plpgsql
as $$
begin
  return to_char(now(), 'YYYYMMDDHH24MISSMS');
end;
$$;
```

## 주문 프로시져

```sql
create or replace function create_order_transaction(
  p_order_name text,
  p_order_email text,
  p_order_phone text,
  p_receiver_name text,
  p_receiver_phone text,
  p_zipcode text,
  p_address text,
  p_address_sub text,
  p_delivery_memo text,
  p_user_id uuid,
  p_items jsonb
)
returns jsonb
language plpgsql
security definer
as $$
declare
  v_order_id uuid;
  v_order_no text;
  v_total_price int := 0;
  v_item record;
  v_product record;
begin
  if p_items is null or jsonb_array_length(p_items) == 0 then
    raise exception '주물할 상품 목록이 비어 있습니다.';
  end if;

  insert into orders (
    order_name, order_email, order_phone,
    receiver_name, receiver_phone, zipcode, address,
    address_sub, delivery_memo, total_price, order_status, user_id
  ) values (
    p_order_name, p_order_email, p_order_phone,
    p_receiver_name, p_receiver_phone, p_zipcode, p_address,
    p_address_sub, p_delivery_memo, 0, 'READY', p_user_id
  )
  returning id, order_no into v_order_id, v_order_no;

  for v_item in
    select
      (elem->>'product_id')::uuid as product_id,
      (elem->>'quantity')::int as quantity
    from jsonb_array_elements(p_items) as elem
  loop
    if v_item.quantity <= 0 then
      raise exception '주문 수량은 1개 이상이어야 합니다.';
    end if;

    select id, name, price
    into v_product
    from product
    where id = v_item.product_id and deleted_at is null;

    if not found then
      raise exception '유효하지 않거나 삭제된 상품이 포함되어 있습니다. (ID: %)', v_item.product_id;
    end if;

    insert into order_items (
      order_id, product_id, item_name, price, quantity
    ) values (
      v_order_id, v_product.id, v_product.name, v_product.price, v_item.quantity
    );

    v_total_price := v_total_price + (v_product.price * v_item.quantity);
  end loop;

  update orders
  set total_price = v_total_price
  where id = v_order_id;

  return jsonb_build_object(
    'success', true,
    'order_id', v_order_id,
    'order_no', v_order_no,
    'total_price', v_total_price
  );
exception
  when others then
    raise exception '주문 처리 실패 (트랜잭션 롤백): %', sqlerrm;
end;
$$;
```
