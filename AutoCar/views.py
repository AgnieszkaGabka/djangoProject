from datetime import datetime, date

from django.contrib.auth import authenticate, login, logout
from django.core.checks import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View

from .forms import AddCarForm, AddChangeForm, RefuelForm, ReplenishForm, LoginForm, CreateUserForm
from .models import Car, Change, Refueling, Replenishment
from django.contrib.auth.models import User


class LoginView(View): #logowanie do aplikacji

    def get(self, request, *args, **kwargs): #pusty formularz do wpisania loginu i hasła
        form = LoginForm()
        context = {
            'form': form
        }
        return render(request, 'login.html', context)

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():#pobieranie danych z formularza i autoryzacja użytkownika
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_authenticated:
                login(request, user) #jeśli użytwkonik jest prawidłowy, przekieruj na stronę główną
                messages.Info(request, "Jesteś zalogowany jako",  {user.username})
                return HttpResponseRedirect('/main/')
        messages.Error(request, "Błędny login lub hasło") #jeśli użytkownik nie został wykryty, przekiruj na stronę logowania
        return HttpResponseRedirect('/login/')


class BaseView(View): #strona główna - nazwa samochodu użytkownika, zestawienie wydatków na ten rok

    def get(self, request):
        current_user = request.user #pobieranie użytkownika z requestu i wyszukiwanie jego samochodu
        try:
            current_car = Car.objects.filter(user=current_user)[0]
        except IndexError:
            return redirect('add_car') #jeśli użytkownik nie ma samochodu, przekieruj na stronę dodawania samochodu
        year = date.today().year #ustawienie obecnego roku
        starting_day_of_current_year = datetime.now().date().replace(month=1, day=1)
        ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)
        fuels = Refueling.objects.filter(car=current_car, fuel_date__range=[starting_day_of_current_year, #wyciągnięcie tankowań dla samochodu uzytkownika w tym roku
                                                                           ending_day_of_current_year])
        fuel_prices = []
        for fuel in fuels:
            fuel_prices.append(int(fuel.amount_fueled)) #dodanie do listy kosztów wszystkich tankowań w obecnym roku
        if fuel_prices:
            fuel_costs = sum(fuel_prices) #koszty tankowania w tym roku
        else:
            fuel_costs = 0
        changes = Change.objects.filter(car=current_car, change_date__range=[starting_day_of_current_year, ending_day_of_current_year]) #wyciągnięcie napraw dla samochodu uzytkownika w tym roku
        changes_prices = []
        for change in changes:
            changes_prices.append(int(change.change_cost)) #dodanie do listy kosztów wszystkich napraw w obecnym roku
        if changes_prices:
            change_costs = sum(changes_prices) #koszty zmian/napraw w tym roku
        else:
            change_costs = 0
        replenishments = Replenishment.objects.filter(car=current_car, date__range=[starting_day_of_current_year, #wyciągnięcie zakupów dla samochodu uzytkownika w tym roku
                                                                       ending_day_of_current_year])
        replenishment_prices = []
        for replenishment in replenishments:
            replenishment_prices.append(int(replenishment.price)) #dodanie do listy kosztów wszystkich zakupów w obecnym roku
        if replenishment_prices:
            replenishment_costs = sum(replenishment_prices) #koszty płynów w tym roku
        else:
            replenishment_costs = 0
        general_costs = int(fuel_costs) + int(change_costs) + int(replenishment_costs) #koszty całkowite w tym roku
        if not general_costs:
            general_costs = 0
        context = {
            'car': current_car,
            'current_user': current_user,
            'fuel_costs': fuel_costs,
            'change_costs': change_costs,
            'replenishment_costs': replenishment_costs,
            'general_costs': general_costs,
            'year': year
        }
        return render(request, 'base.html', context)


class RegisterView(View): #rejestracja nowego użytkownika

    def get(self, request):
        form = CreateUserForm()
        return render(request, 'register.html', {'form': form}) #formularz dodawania użytkownika

    def post(self, request):
        form = CreateUserForm(request.POST)

        if form.is_valid():
            user = form.save() #jeśli dane się zgadzają, utwórz konto

            messages.Info(request, 'Twoje konto zostało utworzone poprawnie')
            return redirect('login')
        context = {'form': form}
        return render(request, 'register.html', context)


class AddCarView(View): #strona dodwania samochodu

    def get(self, request):
        form = AddCarForm() #formularz dodawania samochodu
        return render(request, 'addCar.html', {'form': form})

    def post(self, request):
        form = AddCarForm(request.POST)
        current_user = request.user
        if form.is_valid():
            production_date = form.cleaned_data['production_date']
            brand = form.cleaned_data['brand']
            color = form.cleaned_data['color']
            purchase_date = form.cleaned_data['purchase_date']
            car = Car.objects.create(production_date=production_date, brand=brand, color=color, user=current_user,
                                     purchase_date=purchase_date) #utworzenie samochodu przypisanego do zalogowanego użytkownika
            car.save()
            return redirect(f'/main/') #jeśli samochód utworzony został poprawnie, przekieruj na stronę głowną
        else:
            return render(request, 'addCar.html', {'form': form})


class AddChangeView(View): #dodawanie zmiany/naprawy w samochodzie

    def get(self, request):
        form = AddChangeForm() #formularz dodawania naprawy
        return render(request, 'addChange.html', {'form': form})

    def post(self, request):
        form = AddChangeForm(request.POST)
        if form.is_valid():
            change = form.cleaned_data['change_type']
            c = [str(i) for i in change]
            change_type = str("".join(c)) #wydobycie numeru przypisanego do nazwy naprawy wyświetlonej na stronie
            change_date = form.cleaned_data['change_date']
            change_cost = form.cleaned_data['change_cost']
            car = Car.objects.filter(user=request.user)[0]
            change = Change.objects.create(change_type=change_type, change_date=change_date, change_cost=change_cost,
                                           car=car) #zapisanie zmiany przypisanej do samochodu zalogowanego użytkownika
            return redirect(f'/main/')
        return render(request, 'addChange.html', {'form': form})


class RefuelView(View): #rejestrowanie tankowania paliwa

    def get(self, request):
        form = RefuelForm()#wyświetlenie formularza tankowania
        return render(request, 'refuel.html', {'form': form})

    def post(self, request):
        form = RefuelForm(request.POST)
        if form.is_valid():
            fuel = form.cleaned_data['fuel_type']
            f = [str(i) for i in fuel]
            fuel_type = str("".join(f))#wydobycie numeru przypisanego do paliwa wyświetlonego na stronie
            amount_fueled = form.cleaned_data['amount_fueled']
            amount_paid = form.cleaned_data['amount_paid']
            kilometers_traveled = form.cleaned_data['kilometers_traveled']
            fuel_date = form.cleaned_data['fuel_date']
            car = Car.objects.filter(user=request.user)[0]
            refuel = Refueling.objects.create(fuel_type=fuel_type, amount_fueled=amount_fueled, amount_paid=amount_paid,
                                              kilometers_traveled=kilometers_traveled, car=car, fuel_date=fuel_date)
            return redirect(f'/main/') #zapisanie tankowania przypisanego do samochodu zalogowanego użytkownika i przekierowanie na stronę główną
        return render(request, 'refuel.html', {'form': form})


class ReplenishView(View): #zakupy (płyny, olej itd)

    def get(self, request):
        form = ReplenishForm() #formularz dodawnaia zakupu
        return render(request, 'replenish.html', {'form': form})

    def post(self, request):
        form = ReplenishForm(request.POST)
        if form.is_valid():
            fluid = form.cleaned_data['fluid_type']
            f = [str(i) for i in fluid]
            fluid_type = str("".join(f)) #wydobycie numeru przypisanego do zakupu wyświetlonego na stronie
            price = form.cleaned_data['price']
            date = form.cleaned_data['date']
            car = Car.objects.filter(user=request.user)[0]
            replenish = Replenishment.objects.create(fluid_type=fluid_type, price=price, date=date, car=car) #zapisanie zakupu
            return redirect(f'/main/')
        return render(request, 'replenish.html', {'form': form})


class ReportView(View): #strona z zestawieniem od momentu zakupu samochodu

    def get(self, request):
        current_user = request.user
        car = Car.objects.filter(user=request.user)[0]
        refuels = Refueling.objects.filter(car=car) #wydobycie wszystkich tankowań dla samochodu zalogowanego użytkownika
        if refuels:
            fuels = [] #dodanie kwoty tankowań do listy
            for fuel in refuels:
                fuel_type = fuel.get_fuel_type_display()
                fuels.append(int(fuel.amount_paid))
            fuel_costs = sum(fuels) #zsumowanie wartości tankowań
        else:
            fuel_costs = 0
        changes = Change.objects.filter(car=car) #wydobycie wszystkich napraw dla samochodu zalogowanego użytkownika
        if changes:
            changes_all = []#dodanie kwoty napraw do listy
            for change in changes:
                change_type = change.get_change_type_display()
                changes_all.append(int(change.change_cost))
            changes_costs = sum(changes_all)
        else:
            changes_costs = 0
        fluids = Replenishment.objects.filter(car=car) #wydobycie wszystkich zakupów dla samochodu zalogowanego użytkownika
        if fluids:
            fluids_all = []#dodanie kwoty zakupów do listy
            for fluid in fluids:
                fluid_type = fluid.get_fluid_type_display()
                fluids_all.append(int(fluid.price))
            fluids_costs = sum(fluids_all)
        else:
            fluids_costs = 0
        general_costs = int(fuel_costs) + int(changes_costs) + int(fluids_costs) #zsumowanie wszystkich kosztów
        if not general_costs:
            general_costs = 0
        context = {
            'current_user': current_user,
            'car': car,
            'refuels': refuels,
            'fuel_type': fuel_type,
            'change_type': change_type,
            'fluid_type': fluid_type,
            'changes': changes,
            'fluids': fluids,
            'fuel_costs': fuel_costs,
            'changes_costs': changes_costs,
            'fluids_costs': fluids_costs,
            'general_costs': general_costs
        }
        return render(request, 'report.html', context)


class LogoutUserView(View): #wylogowanie użytkownika
    def get(self, request):
        logout(request)
        messages.Info(request, 'Jesteś wylogowany')
        return redirect('/login/')
