# 🎮 **Transcendence Projesi**

## 🚀 **Genel Bakış**

**Transcendence**, 42 İstanbul’da geliştirdiğim bir projedir. Bu projede çeşitli teknolojiler kullanarak iki oyunculu bir oyun ve turnuva sistemi oluşturulmuştur. Ayrıca, proje boyunca mikroservis mimarisi kullanılmıştır. Gerçek zamanlı etkileşim, sohbet sistemi ve güvenlik özellikleriyle kullanıcılar arasında dinamik ve güvenli bir deneyim sunulmaktadır.

## 🛠️ **Kullanılan Teknolojiler**

- 🐍 **Django**: Backend geliştirmesi için kullanıldı. REST API'ler ve WebSocket bağlantıları burada sağlandı.
- 🌐 **VanillaJS**: Frontend'de dinamik içerik ve kullanıcı etkileşimleri için saf JavaScript kullanıldı.
- 🐳 **Docker**: Uygulamanın kolay kurulumu ve çalıştırılması için konteynerize edildi.
- ⚙️ **Nginx**: Uygulamanın statik dosyalarını sunmak ve yük dengelemesi için kullanıldı.
- 🔄 **WebSocket**: Gerçek zamanlı iletişim sağlamak amacıyla hem oyun hem de sohbet sisteminde kullanıldı.
- 🔑 **42auth**: 42 Ekosistemi'ne entegre edilmiş oturum açma ve kullanıcı doğrulama sistemi.
- 🛡️ **2FA (Two-Factor Authentication)**: Kullanıcı hesaplarının güvenliği için iki aşamalı doğrulama sistemi kullanıldı.
- 🧩 **JWT (JSON Web Token)**: Kullanıcı kimlik doğrulama ve oturum yönetimi için kullanıldı.

## 🎯 **Proje Özellikleri**

- 🎮 **İki Kişilik Oyun**: İki kullanıcı arasında gerçek zamanlı olarak oynanabilen bir oyun.
- 🏆 **Turnuva Sistemi**: Birden fazla kullanıcının katılabileceği turnuvalar düzenlenebilir.
- 💬 **Sohbet Sistemi**: Kullanıcılar oyun sırasında veya dışarıda birbirleriyle gerçek zamanlı sohbet edebilir.
- 🧩 **Mikroservis Mimarisi**: Proje, farklı işlevleri bağımsız servisler olarak çalıştıracak şekilde tasarlandı. Bu sayede esneklik ve ölçeklenebilirlik sağlandı.
- 🔐 **Güvenlik**: 42auth, 2FA ve JWT sistemleri kullanılarak kullanıcıların güvenli bir şekilde oturum açması ve işlemlerini gerçekleştirmesi sağlandı.

## ⚙️ **Kurulum**

### 📋 **Gereksinimler**

- **Docker** ve **Docker Compose** kurulu olmalıdır.

### 🚀 **Kurulum Adımları**

1. Projeyi klonlayın:
    ```bash
   https://github.com/fsoymaz/TRANSCENDENCE.git
    ```
    
2. Projede bir `.env` dosyası oluşturup kendi bilgilerinizi girmeniz gerekmektedir. Django projelerinde settings dosyaları ve docker-compose dosyasındaki gizli veriler `.env` dosyasında saklanır.

3. **Nginx Konfigürasyonu**:

   - **Domain veya localhost**: Eğer bir domain ismine sahipseniz, Nginx yapılandırma dosyasındaki (`default.conf`) ilgili kısma domaininizi yazın. Eğer projenizi localde çalıştırıyorsanız, bu kısmı `localhost` olarak ayarlayabilirsiniz.

   - **Frontend ile Backend arasındaki istekler**: Frontend'den backend'e istek atarken, eğer domain üzerinden yapıyorsanız, tüm isteklerin bu domain üzerinden gönderildiğinden emin olun. Aksi takdirde, yanlış yapılandırmalar sebebiyle hatalarla karşılaşabilirsiniz.

   - **IP Değişiklikleri**: Nginx içinde kullanılan IP adresini değiştirmek için:
     - VSCode'da arama yaparak Nginx yapılandırma dosyasındaki IP adresini bulun.
     - Bulduğunuz IP adresini projenizin domaini veya kullanmak istediğiniz yeni IP adresiyle değiştirin.
     - Tüm dosyalarda bu değişikliği yapmayı unutmayın.
   
   - **SSL Sertifikası**: Projenizin güvenliği için SSL sertifikası almayı ihmal etmeyin. Bu, özellikle domain üzerinden erişim sağlıyorsanız önemlidir ve projenizi HTTPS ile güvenli hale getirecektir.

4. Docker konteynerlerini başlatın:
    ```bash
    docker-compose up --build || make
    ```

5. Uygulamaya tarayıcıdan erişin:
    ```
    https://localhost:80 || https://your_domain
    ```

---

🎉 **Keyifli kullanımlar!**
