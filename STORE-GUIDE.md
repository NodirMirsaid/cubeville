# Как выложить Cubeville в App Store и Google Play

Приложение уже собрано и лежит в репозитории:

| Что | Где |
|---|---|
| Проект iOS и Android (Capacitor 8): игра, шрифт, 3D-движок и связь с сервером внутри, без загрузок из интернета | `app/` |
| Облачная сборка обеих версий | `codemagic.yaml` |
| Тексты, ответы на анкеты, скриншоты, баннер | `store/` |
| Политика конфиденциальности | https://nodirmirsaid.github.io/cubeville/privacy.html |
| Страница поддержки и удаления аккаунта | https://nodirmirsaid.github.io/cubeville/help.html |

Mac не нужен: обе версии собирает Codemagic в облаке.

Тебе остаются шаги, которые делает только владелец аккаунтов. Порядок такой: подготовь Supabase (шаг 0), заведи оба аккаунта сразу, потому что их проверка идёт параллельно, а дальше иди по шагам.

---

## 0. Сначала, 5 минут: Supabase
Без этого магазины откажут: Apple и Google требуют, чтобы аккаунт можно было удалить прямо в игре.

1. Supabase → **SQL Editor** → вставь и нажми **Run**:
   ```sql
   create or replace function public.delete_my_account() returns void
   language plpgsql security definer set search_path = public, auth as $$
   begin
     if auth.uid() is null then raise exception 'not signed in'; end if;
     delete from auth.users where id = auth.uid();
   end $$;
   revoke all on function public.delete_my_account() from public, anon;
   grant execute on function public.delete_my_account() to authenticated;
   ```
2. **Authentication → Sign In / Providers → Email** → выключи **Confirm email**.
3. **Realtime → Settings** → выключи **Allow public access**.

## 1. Аккаунты разработчика
**Apple Developer Program**, $99 в год:
1. developer.apple.com/programs → **Enroll**.
2. Тип: **Individual**. В магазине будет видно твоё имя, а для организации понадобился бы D-U-N-S.
3. Нужен Apple ID с двухфакторной защитой и банковская карта. Проверка занимает от нескольких часов до 2 дней.

**Google Play Console**, $25 один раз:
1. play.google.com/console → создай **личный (Personal)** аккаунт.
2. Подтверди личность документом. Это занимает до нескольких дней.
3. ⚠️ Правило для новых личных аккаунтов: перед публикацией нужно **закрытое тестирование: не меньше 12 тестеров и 14 дней подряд**. Тестерами могут быть ты, жена, дочка, родители подружек — любые аккаунты Google. Поэтому Google Play займёт минимум 2 недели, тут ничего не ускорить.

**Почта для связи:** магазины покажут её на странице игры. Заведи отдельную, например cubeville.help@gmail.com, и напиши её мне. Я впишу её на страницу поддержки.

## 2. App Store: создать приложение
1. developer.apple.com → Certificates, IDs & Profiles → **Identifiers** → «+» → App IDs → App → Bundle ID: `uz.nodir.cubeville`, Description: Cubeville.
2. appstoreconnect.apple.com → Apps → «+» → **New App**:
   - Platform: iOS;
   - Name: `Cubeville: мир для детей`. Если имя занято, добавь что-то своё;
   - Primary language: Russian;
   - Bundle ID: `uz.nodir.cubeville`;
   - SKU: `CUBEVILLE001`.
3. Открой **App Information**. Скопируй число **Apple ID** (например, 6739012345): оно понадобится на шаге 3.

## 3. Codemagic: сборка iOS
1. codemagic.io → войди через GitHub → **Add application** → репозиторий `NodirMirsaid/cubeville` → тип **Other** (codemagic.yaml).
2. В App Store Connect открой **Users and Access → Integrations → App Store Connect API**:
   - создай ключ с ролью **App Manager**;
   - скачай `.p8`;
   - запиши **Issuer ID** и **Key ID**.
3. Codemagic → Team settings → **Integrations → Developer Portal** → Connect → вставь ключ и **назови его `codemagic`**: это имя указано в `codemagic.yaml`.
4. Codemagic → Team settings → **Code signing identities → iOS certificates** → **Generate certificate** (тип Apple Distribution).
5. В той же вкладке открой **iOS provisioning profiles** → **Fetch profiles**. Если профиля для `uz.nodir.cubeville` нет, создай его там же: App Store, `uz.nodir.cubeville`.
6. В файле `codemagic.yaml` замени `APP_STORE_APPLE_ID: 0` на число из шага 2.3. Можешь просто прислать число мне — я поменяю.
7. **Start new build** → workflow **iOS → TestFlight**. Через 15–25 минут сборка появится в App Store Connect → TestFlight.

## 4. TestFlight: проверить на iPhone
1. App Store Connect → Cubeville → **TestFlight** → Internal Testing → добавь себя.
2. Установи приложение **TestFlight** из App Store и открой в нём Cubeville.
3. Проверь:
   - регистрацию и вход;
   - что два телефона видят друг друга в одной локации;
   - кнопку 🛡️ → пример → «Удалить игрока».

## 5. App Store: заполнить страницу и отправить
Всё бери из `store/STORE-LISTING.md`.
1. **App Information:**
   - Category: Games, вторичная Family;
   - **Kids Category: 9–11**;
   - Privacy Policy URL.
2. **Pricing and Availability:** Free, все страны.
3. **App Privacy:** таблица из файла.
4. **Age Rating:** ответы из файла.
5. **Версия 1.0:**
   - скриншоты: `store/screenshots/ios-iphone-6.9` (5 штук) и `ios-ipad-13` (5 штук);
   - описание, ключевые слова, Support URL, промо-текст;
   - Build: выбери сборку из TestFlight;
   - App Review Information: Sign-in required **No**, Notes — текст из файла.
6. **Add for Review → Submit**. Проверка обычно занимает 1–3 дня. Детские приложения проверяют строже, но всё нужное уже есть:
   - родительский барьер;
   - нет внешних ссылок, рекламы и аналитики;
   - удаление аккаунта;
   - общение только смайликами.

## 6. Google Play: ключ подписи
Ключ загрузки я уже создал: это файл `cubeville-upload.jks` и пароль, оба в чате. **Сохрани их в надёжном месте**, например в менеджере паролей и на облачном диске. Без этого ключа не выйдет обновлять игру. Восстановить его можно только через поддержку Google.

1. Codemagic → Team settings → **Code signing identities → Android keystores** → **Add keystore**:
   - файл: `cubeville-upload.jks`;
   - Keystore password и Key password: пароль из чата;
   - Key alias: `cubeville`;
   - **Reference name: `cubeville_upload`**.
2. Codemagic → **Start new build** → workflow **Android → Google Play**.
   - Первый раз шаг публикации упадёт: это нормально, приложения в Google Play ещё нет.
   - Скачай файл `.aab` из Artifacts.

## 7. Google Play: создать приложение
1. Play Console → **Create app**:
   - имя `Cubeville: мир для детей`;
   - язык Русский;
   - Game, Free;
   - отметь подтверждения.
2. **Dashboard → Set up your app.** Пройди все пункты, ответы есть в `store/STORE-LISTING.md`:
   - Privacy policy;
   - App access: всё доступно без входа;
   - Ads: No;
   - Content rating;
   - Target audience: 6–8, 9–12;
   - Data safety;
   - **Delete account URL**.
3. **Main store listing:**
   - короткое и полное описание;
   - иконка 512×512: `icon-512.png` из репозитория;
   - Feature graphic: `store/screenshots/android-feature-graphic-1024x500.png`;
   - скриншоты телефона: `store/screenshots/android-phone` (5 штук).
4. **Testing → Closed testing:**
   - Create track;
   - загрузи `.aab` из шага 6;
   - добавь 12+ тестеров по почте Google;
   - отправь на проверку.
   - Тестеры ставят приложение по ссылке и **14 дней** держат его установленным.
5. Через 14 дней на главной Play Console появится **Apply for production** → ответь на вопросы о тестировании → после одобрения выпусти версию в Production.

Чтобы следующие сборки сами попадали в Google Play:
1. Google Cloud → создай Service Account с JSON-ключом.
2. Play Console → Users and permissions → пригласи его (Release manager).
3. Codemagic → Environment variables → группа **`google_play`** → переменная `GCLOUD_SERVICE_ACCOUNT_CREDENTIALS` = содержимое JSON (отметь Secret).

## Обновления игры
Я меняю `game.html` и запускаю сборку сайта. Чтобы обновить приложения, в Codemagic нажми **Start new build** для каждой платформы. Номера сборок растут сами.
- В App Store новая версия ждёт отправки на проверку: повысь Version (1.0 → 1.1) в App Store Connect.
- В Google Play новая версия попадает в Internal testing: оттуда её можно продвинуть в Production.

## Что проверено, а что нет
- ✅ Игра внутри приложения не загружает ничего из интернета:
  - шрифт, 3D и библиотеки свои;
  - 0 запросов к сторонним сайтам, кроме своего сервера Supabase.
- ✅ Родительский барьер, страницы политики и поддержки, скриншоты нужных размеров.
- ⚠️ Сами сборки iOS и Android ещё не запускались: в моей среде нет Xcode и Android SDK. Первая сборка в Codemagic это покажет. Если что-то упадёт, пришли лог, и я поправлю.
